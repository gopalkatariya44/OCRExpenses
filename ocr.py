import boto3
from config import settings


class SmartExpenseTask:
    def __init__(self) -> None:
        self.s3 = boto3.client(
            's3', region_name=settings.REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.textract = boto3.client(
            'textract', region_name=settings.REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    # Function to create an S3 bucket
    def create_s3_bucket(self):
        self.s3.create_bucket(Bucket=self.bucket_name, CreateBucketConfiguration={
            'LocationConstraint': settings.REGION_NAME
        }, )
        print(f"Bucket '{self.bucket_name}' created successfully.")

    # Function to upload a document to the S3 bucket
    def upload_document_to_s3(self, document_name, file_path):
        self.s3.upload_file(file_path, self.bucket_name, document_name)
        print(f"Document '{document_name}' uploaded to the bucket.")

    def startAnalyseJob(self, object_name):
        response = self.textract.start_expense_analysis(
            DocumentLocation={
                'S3Object': {
                    'Bucket': self.bucket_name,
                    'Name': object_name
                }
            })
        return response["JobId"]

    def check_textract_job_status(self, job_id):
        response = self.textract.get_expense_analysis(
            JobId=job_id,
            MaxResults=123,
            # NextToken='string'
        )
        status = response['JobStatus']
        print(f"Status : {status} ")
        return status, response

    @staticmethod
    def analyze_expenses(textract_response):
        dic = {"title": "", "amount": 0}
        for item in textract_response['ExpenseDocuments'][0]['SummaryFields']:
            if item['Type']['Text'] == "NAME":
                if item['ValueDetection']['Text'] != "":
                    dic['title'] = item['ValueDetection']['Text']
            if item['Type']['Text'] == "SUBTOTAL":
                if item['ValueDetection']['Text'] != "":
                    dic['amount'] = item['ValueDetection']['Text']
        return dic

    # Main function
    def main(self, document_name, file_path):
        # self.create_s3_bucket()
        self.upload_document_to_s3(document_name, file_path)
        job_id = self.startAnalyseJob(document_name)
        print(f"Started Textract job with JobId: {job_id}")
        status, response = self.check_textract_job_status(job_id)
        while status == 'IN_PROGRESS':
            status, response = self.check_textract_job_status(job_id)
        if status == 'SUCCEEDED':
            final_ans = self.analyze_expenses(response)
            return final_ans
        else:
            print(f"Textract job failed with status: {status}")
