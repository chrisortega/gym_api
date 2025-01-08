const express = require('express');
const mysql = require('mysql2');
const cors = require('cors'); // Import the CORS middleware
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const nodemailer = require('nodemailer');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const twilio = require('twilio');
//https://medium.com/@rahulvikhe25/deployment-of-node-js-application-on-ec2-with-ci-cd-using-github-actions-and-docker-container-46c3efa2905f

const app = express();
const PORT = process.env.GYM_DB_PORT;

// Middleware
app.use(cors()); // Enable CORS
var bodyParser = require('body-parser');
app.use(bodyParser.json({ limit: '5mb' }));
app.use(bodyParser.urlencoded({ limit: '5mb', extended: true, parameterLimit: 5000 }));

// Database connection
const db = mysql.createConnection({
  host: process.env.GYM_DB_SERVER, // Update with your MySQL host
  user: process.env.GYM_DB_USERNAME,      // Update with your MySQL username
  password: process.env.GYM_DB_PASSWORD,      // Update with your MySQL password
  database: process.env.GYM_DB_NAME    // Update with your MySQL database name
});

const SECRET_KEY = process.env.SECRET_KEY;

// Set up multer for image upload

const storage = multer.memoryStorage(); // Store images in memory
const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 } // 5 MB limit
});



// Connect to the database
db.connect((err) => {
  if (err) {
    console.error('Error connecting to MySQL:', err.message);
    process.exit(1);
  }
  console.log('Connected to MySQL database.');
});


function generateAccessToken  (userId) {
  return jwt.sign({ userId }, SECRET_KEY, { expiresIn: "7d" });
};

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];

  // Extract token
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ message: "Access token missing" });

  // Verify token
  jwt.verify(token, SECRET_KEY, (err, user) => {
    if (err) return res.status(403).json({ message: "Invalid token" });

    // Attach user to request object
    req.user = user;
    next();
  });
}







app.post('/users', (req, res) => {
  const { name, exp, gym_id } = req.body;
  
  const query = `
    INSERT INTO users (name, exp, gym_id)
    VALUES (?, ?, ?)
  `;
  const values = [name, exp, gym_id];

  db.query(query, values, (err, result) => {
    if (err) {
      console.error('Error inserting user:', err);
      return res.status(500).json({ error: 'Database error.' });
    }

    const insertedId = result.insertId;
    res.status(200).json({ 
      message: 'User inserted successfully.', 
      id: insertedId 
    });
  });
});

// Endpoint to update just the image field
app.put('/update-user-image/:id', upload.single('image'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No image uploaded.');
  }

  const gymId = req.params.id;
  const imageData = req.file.buffer;
  const query = 'UPDATE users SET image = ? WHERE id = ?';
  db.query(query, [imageData, gymId], (err, result) => {
    if (err) {
  
      return res.status(500).send('Error updating image.');
    }

    if (result.affectedRows === 0) {
      return res.status(404).send('User not found.');
    }

    res.status(200).send('image updated successfully');
  });
});;




// Endpoint to update just the image field
app.put('/update-image/:id', upload.single('image'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No image uploaded.');
  }

  const gymId = req.params.id;
  const imageData = req.file.buffer;

  const query = 'UPDATE gym SET image = ? WHERE id = ?';
  db.query(query, [imageData, gymId], (err, result) => {
    if (err) {
      console.error('Error updating image:', err);
      return res.status(500).send('Error updating image.');
    }

    if (result.affectedRows === 0) {
      return res.status(404).send('Gym not found.');
    }

    res.status(200).send('Image updated successfully');
  });
});;





app.put('/users', authenticateToken, (req, res)=>{
  const { id, name, exp } = req.body;

  if (!id || !name || !exp) {
    return res.status(400).json({ error: 'All fields (id, name, exp) are required.' });
  }
  // Format the date to 'YYYY-MM-DD'
  const formattedExp = new Date(exp).toISOString().split('T')[0];

  // Check if the user already exists
  const checkQuery = 'SELECT * FROM users WHERE id = ?';
  db.query(checkQuery,  [id], (err, results) => {
    if (err) {
      console.error('Error checking user:', err);
      return res.status(500).json({ error: 'Database error.' });
    }

    if (results.length > 0) {
      // User exists, update the record
      const updateQuery = 'UPDATE users SET name = ?, exp = ? WHERE id = ?';
      db.query(updateQuery, [name, formattedExp, id], (updateErr) => {
        if (updateErr) {
          console.error('Error updating user:', updateErr);
          return res.status(500).json({ error: 'Database error.' });
        }
        res.status(200).json({ message: 'User updated successfully.' });
      });
    } else {

    }
  });
});

// 3. Register a user entry
app.post('/entries', authenticateToken, async (req, res) => {
  const { user_id, gym_id } = req.body;
  var flag1 = await userBelongsToGym(user_id, gym_id)
  if (!flag1){
    return res.status(426).send("Este usuario no esta en este gymnasio");
   }

  const query = `INSERT INTO entries (users_id,gym_id) VALUES (?,?)`;
  db.query(query, [user_id, gym_id], (err, results) => {
    if (err) return res.status(500).send(err.message);
    res.status(201).json({ id: results.insertId, user_id, entry_date: new Date().toISOString().split('T')[0] });
  });
});

// 4. Get all gyms
app.get('/gyms', authenticateToken, (req, res) => {
  const query = `SELECT * FROM gym`;
  db.query(query, (err, results) => {
    if (err) return res.status(500).send(err.message);
    res.json(results);
  });
});

// 4. Get all gyms
app.get('/gym/:id', authenticateToken, (req, res) => {
  const query = `SELECT * FROM gym WHERE id = ?`;
  const userId = req.params.id;
  db.query(query, [userId], (err, results) => {
    if (err) return res.status(500).send(err.message);
    res.json(results);
  });
});

// 5. Get all users of a gym
app.get('/users/gym/:gymId', authenticateToken, (req, res) => {
  const gymId = req.params.gymId;

  const query = `
    SELECT users.*
    FROM users 
    JOIN gym ON users.gym_id = gym.id
    where gym_id = ?

  `;
  db.query(query,[gymId], (err, results) => {
    if (err) return res.status(500).send(err.message);
    res.json(results);
  });
});

// 5. Get all users
app.get('/users', authenticateToken, (req, res) => {
  
  const query = `
    SELECT users.*
    FROM users 
    JOIN gym ON users.gym_id = gym.id

  `;
  db.query(query, (err, results) => {
    if (err) return res.status(500).send(err.message);
    res.json(results);
  });
});

// 6. Get all entries
app.get('/entries', authenticateToken, (req, res) => {
  const query = `
    SELECT entries.*, users.name 
    FROM entries 
    JOIN users ON entries.users_id = users.id
  `;
  db.query(query, (err, results) => {
    if (err) return res.status(500).send(err.message);
    res.json(results);
  });
});

//  Get all entries for today
app.get('/entries', authenticateToken, (req, res) => {
    const query = `
      SELECT entries.*, users.name 
      FROM entries 

    `;
    db.query(query, (err, results) => {
      if (err) return res.status(500).send(err.message);
      res.json(results);
    });
  });
  app.get('/entries/today/:gymid',  authenticateToken, (req, res) => {
    const gymid = req.params.gymid;
    const { limit = 10, offset = 0 } = req.query;
  
    const query = `
      SELECT entries.*, users.name, users.exp , users.image, users.id as user_id
      FROM entries 
      JOIN users ON entries.users_id = users.id
      JOIN gym ON entries.gym_id = gym.id 
      WHERE DATE(day) = CURDATE() and gym.id = ?
      LIMIT ? OFFSET ?
    `;
  
    db.query(query, [gymid,parseInt(limit), parseInt(offset)], (err, results) => {
      if (err) return res.status(500).send(err.message);
      res.json(results);
    });
  });



  function userBelongsToGym(user_id, gym_id){
    const query = `SELECT users.id FROM gyms.users where users.id = ? and gym_id=?;`;
   return new Promise((resolve, reject) => {
     db.query(query, [user_id, gym_id], (err, results) => {
       if (err) {
         
         resolve(false);
       } else if (results.length === 0) {
         
         resolve(false);
       } else {
        resolve(true);
        
       }
     });
   });

   return false
  }

  function getGymByAdmin(admin_id){
    const query = `
    SELECT gym.*
     FROM gym
     WHERE gym.admin_id  = ?
   `;
   return new Promise((resolve, reject) => {
     db.query(query, [admin_id], (err, results) => {
       if (err) {
         return []
       } else if (results.length === 0) {
         return []
       } else {
         resolve(results[0]); // Return the first result since ID is unique
       }
     });
   });

   return res.results 
  }

  function getadminByEmail(email){
    const query = `
     SELECT admin.*
      FROM admin
      WHERE admin.email  = ?
    `;
    return new Promise((resolve, reject) => {
      db.query(query, [email], (err, results) => {
        if (err) {
          return []
        } else if (results.length === 0) {
          return []
        } else {
          resolve(results[0]); // Return the first result since ID is unique
        }
      });
    });

    return res.results
  }


  

  function getUser(userId) {
    const query = `
      SELECT users.*, gym.name as gym_name
      FROM users  
      JOIN gym on users.gym_id = gym.id
      WHERE users.id = ?
    `;
  
    return new Promise((resolve, reject) => {
      db.query(query, [userId], (err, results) => {
        if (err) {
          //reject(new Error(err.message));
          resolve([]);
        } else if (results.length === 0) {
          //reject(new Error('User not found'));
          resolve([]);
        } else {
          resolve(results[0]); // Return the first result since ID is unique
        }
      });
    });
  }



  function getUserEntries(userId) {
    const query = `
   SELECT entries.*, users.*, gym.name as gym_name
      FROM entries
      JOIN users ON entries.users_id = users.id 
      JOIN gym ON entries.gym_id = gym.id 
      WHERE entries.users_id = ?
    `;
  
    return new Promise((resolve, reject) => {
      db.query(query, [userId], (err, results) => {
        if (err) {
          resolve([]);
        } else if (results.length === 0) {
          resolve ([]);
        } else {
          resolve(results); // Return the first result since ID is unique
        }
      });
    });
  }


  app.get('/entries/:id',  async (req, res) => {
    const userId = req.params.id;
    const result = await getUserEntries(userId);
    return res.status(200).json(result);


  });
  
// Get a user by  ;;;;;
app.get('/users/:id',   async (req, res) => {
    const userId = req.params.id;
    const user = await getUser(userId);
    
    return res.status(200).json(user);

  });



  
  app.post('/login',  async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
       return  res
        .status(400)
        .json({ error: "Email or Password fields cannot be empty!" });
     
    }
    const user = await getadminByEmail(email);
    
    if (user.length <= 0) {
      return  res
        .status(403)
        .json({ error: "invalid" }); 
    }
    const passwordMatch = await bcrypt.compare(
      password,
      user.password
    );


    if (passwordMatch) {
      const gym = await getGymByAdmin(user.id)
     return res.status(200).json({
        userId: user.id,
        email: user.email,
        access_token: generateAccessToken(user.userId),     
        image: gym.image,
        gym_name: gym.name,  
        gym_id: gym.id, 
      });
    } else {
     return res.status(401).json({ error: "Invalid credentials" });
    }

   return res.status(400).json({ error: "bad request" });
  });

  function isValidPassword(password) {
    // Define validation criteria
    const minLength = 8; // Minimum length
    const maxLength = 20; // Optional maximum length

    const hasUpperCase = /[A-Z]/.test(password); // At least one uppercase letter
    const hasLowerCase = /[a-z]/.test(password); // At least one lowercase letter
    const hasNumber = /\d/.test(password); // At least one number
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password); // At least one special character
    const isValidLength = password.length >= minLength && password.length <= maxLength;

    // Combine all checks
    return isValidLength && hasUpperCase && hasLowerCase && hasNumber && hasSpecialChar;
}

  async function hashPassword(password) {
    if (isValidPassword(password)) {
      const salt = await bcrypt.genSalt(10); // Await the salt generation
      const hashedPassword = await bcrypt.hash(password, salt); // Await the password hashing
      return hashedPassword;
  } else {
      console.log("Password is invalid. Please try again.");
      return null
  }

  }
    app.put('/resetPassword', authenticateToken, (req, res) => {
        const { email, password, token } = req.body;

        bcrypt.genSalt(10)
        .then(salt => {
            return bcrypt.hash(password, salt); // Use resolved salt
        })
        .then(hashedPassword => {
        
            const query = `UPDATE admin SET password = ? WHERE email = ?`;

            const params = [hashedPassword, email];
            db.query(query, params, (err, results) => {
                if (err) {
                    console.error("Database error:", err);
                    return res.status(500).json({ error: "Internal server error" });
                }
    
                if (results.affectedRows === 0) {
                    return res.status(404).json({ error: "User not found" });
                }
    
                res.json({ message: "Password updated successfully" });
            });

        })
        .catch(error => {
            console.error("Error hashing password:", error);
        });



    } );


    
    
    app.post('/update-user',authenticateToken, upload.single('image'), (req, res) => {
      const { id, name, exp, gym_id,image } = req.body;
      const imageData = req.file ? req.file.buffer : null;
      const params = [name, exp, gym_id];

      var query = `
      UPDATE gyms.users 
      SET name = ?, exp = ?, gym_id = ?
      WHERE id = ?`;
      
      if (image){
          // Decode Base64 file content
          const matches = image.match(/^data:(.+);base64,(.+)$/);
          if (!matches) {
            return res.status(400).send({ error: 'Invalid file format' });
          }

          const fileType = matches[1]; // e.g., "image/png"
          const fileContent = Buffer.from(matches[2], 'base64');          
        query = `
        UPDATE gyms.users 
        SET name = ?, exp = ?, gym_id = ?, image = ? 
        WHERE id = ?`;
        params.push(fileContent);
      }

    
      params.push(id);
      
    
      db.query(query, params, (err, result) => {
        if (err) {
          console.error('Error updating user:', err);
          return res.status(500).send('Error updating user.');
        }
    
        if (result.affectedRows === 0) {
          return res.status(404).send('User not found.');
        }
    
        res.status(200).send('User updated successfully');
      });
    });
    

    function generateVerificationCode() {
      return Math.floor(1000 + Math.random() * 9000); // Ensures a 4-digit number
    }
    

    //pending
    app.post('/send-password-code', authenticateToken, (req, res) => {
      const {  email, id } = req.body;
      //const accountSid = 'x';
      //const authToken = 'x';
      //const client = require('twilio')(accountSid, authToken);
      const verificationCode = generateVerificationCode();
        /* 
      client.messages
          .create({
            body: `Tu codigo es: ${verificationCode}`,
            from: '+x', // Replace with your Twilio number
            to: '+x',   // Replace with the recipient's number
          })
          .then(message => console.log(`Message sent: ${message.sid}`))
          .catch(error => console.error('Error sending message:', error));
          */
          const updateQuery = 'UPDATE `gyms`.`admin` SET `verify_code` = ?,  `verify_code_exp` = DATE_ADD(NOW(), INTERVAL 2 HOUR) WHERE `id` = ? and email = ?;';
          db.query(updateQuery, [verificationCode, id, email], (updateErr) => {
            if (updateErr) {
            
              return res.status(500).json({ error: 'Database error.' });
            }
            return res.status(200).json({ "code":"is sent on email" });
          });
          

    }

          
  )
  app.post('/verify-code', authenticateToken, async (req, res) => {
    const { code, email, id, newpassword } = req.body;    
    const query = `
      UPDATE gyms.admin
      SET verify_code = NULL, password = ?
      WHERE id = ? AND email = ? AND verify_code = ? AND verify_code_exp > NOW();
    `;  
    if (newpassword === undefined){
      return res.status(400).json({ error: 'Invalid or expired verification code' });
    }
    const hashedPassword = await hashPassword(newpassword);  
    if (hashPassword === null){
      return res.status(400).json({ error: 'Invalid or expired verification code' });
    }
    
     db.query(query, [hashedPassword ,id, email, parseInt(code)], (err, result) => {
      if (err) {        
        return res.status(500).json({ error: 'Database error' });
      }
  
      // If no rows were affected, the code is either incorrect or expired
      if (result.affectedRows === 0) {
        return res.status(400).json({ error: 'Invalid or expired verification code' });
      }
  
      // If the code was successfully invalidated, the verification was successful

      res.status(200).json({ message: 'Verification successful' });
    });
  });


  app.put('/update-gym', authenticateToken,  (req, res) => {
    const { name, gym_id, image } = req.body;
    const imageData = req.file ? req.file.buffer : null;
    const params = [name];



    var query = `
    UPDATE gyms.gym 
    SET name = ?
    WHERE id = ?`;
    if (image){
      // Decode Base64 file content
      const matches = image.match(/^data:(.+);base64,(.+)$/);
      if (!matches) {
        return res.status(400).send({ error: 'Invalid file format' });
      }

      const fileType = matches[1]; // e.g., "image/png"
      const fileContent = Buffer.from(matches[2], 'base64'); 
      query = `
      UPDATE gyms.gym 
      SET name = ?, image = ? 
      WHERE id = ?`;
      params.push(fileContent);
    }

    params.push(gym_id);
    
  
    db.query(query, params, (err, result) => {
      if (err) {
        console.error('Error updating gym:', err);
        return res.status(500).send('Error updating user.');
      }
  
      if (result.affectedRows === 0) {
        return res.status(404).send('gym not found.');
      }
  
      res.status(200).send('gym updated successfully');
    });
  });


app.listen(process.env.PORT || 3000, function () {
  console.log("The server has started successfully");
});