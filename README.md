## TempCheck
### A python application for monitoring temperature
#### The following python packages need to be installed:
  - fastapi
  - pydantic
  - SQLAlchemy
  - cryptography
  - plotly
  - bcrypt
  - python-jose
  - passlib
  - pandas
  - uvicorn
  - kaleido
  - python-multipart
  - firebase-admin

#### Change sensor data retrieval
To change the way data is retrieved from your sensor modify the `check_data` method in the `sensor` package
#### Run
To run the server use the following command:

    uvicorn api.main:app
    
