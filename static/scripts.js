document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
  });


  async function loadHtmlIntoDiv(divId, filePath) {
    try {
      const response = await fetch(filePath);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const htmlText = await response.text();
      document.getElementById(divId).innerHTML = htmlText;
    } catch (error) {
      console.error('Error loading HTML:', error);
    }
  }