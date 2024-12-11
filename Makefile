doc:
	https://docs.streamlit.io/develop/tutorials/databases/aws-s3

aws:
	aws configure
	aws s2 ls
	aws s3 cp architecture-mlflow.png s3://test-tcc

streamlit:
	streamlit run main.py --server.enableXsrfProtection false
