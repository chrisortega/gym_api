from routes.auth import generate_verification_code

def test_generate_verification_code_default_length():
    """Test that the default verification code is 6 digits long."""
    code = generate_verification_code()
    assert len(code) == 6
    assert code.isdigit()

def test_generate_verification_code_custom_length():
    """Test that the verification code respects the length parameter."""
    code = generate_verification_code(8)
    assert len(code) == 8
    assert code.isdigit()

def test_generate_verification_code_randomness():
    """Test that consecutive verification codes are likely different."""
    code1 = generate_verification_code()
    code2 = generate_verification_code()
    # While it's theoretically possible for them to be the same, 
    # the probability is 1 in a million, so this is safe enough for a basic check
    assert code1 != code2
