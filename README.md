## Steps


### Activate VirtualEnv
`source <virtual env>/bin/activate`


### Install Dependencies
`pip3 install -r requirements.txt`


### Start Backend
```
cd src/backend
uvicorn main:app --reload
```
go to **/docs** to access API List


### Start Frontend
```
cd src/frontend
streamlit run app.py
```