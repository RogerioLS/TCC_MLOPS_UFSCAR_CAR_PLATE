aws:
	aws configure
	aws s2 ls
	aws s3 cp architecture-mlflow.png s3://test-tcc

streamlit:
	streamlit run mani.py --server.enableXsrfProtection falsecd