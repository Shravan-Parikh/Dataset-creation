import streamlit as st
import boto3
import psycopg2

# AWS credentials
AWS_ACCESS_KEY_ID = 'AKIA47CR2RFZRWOMIIGO'
AWS_SECRET_ACCESS_KEY = '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'
S3_BUCKET_NAME = 'image-testing-pipeline'

# Database connection
DB_HOST = 'localhost'
DB_NAME = 'payload'
DB_USER = 'postgres'
DB_PASSWORD = 'root'

# Function to upload image to S3 bucket
def upload_to_s3(file):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    try:
        s3.upload_fileobj(file, S3_BUCKET_NAME, file.name)
        return True
    except Exception as e:
        st.error(f"Error uploading file: {e}")
        return False

# Function to insert data into PostgreSQL database
def insert_into_db(file_url , attachment_type , visual_classification, nutrition_extraction,bodypart_analysis,text_classification ,text_extraction, labreport_extraction,output,history):
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                            user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Entry ( file_url , attachment_type , visual_classification, nutrition_extraction,bodypart_analysis,text_classification ,text_extraction, labreport_extraction,output,history)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """, ( file_url , attachment_type , visual_classification, nutrition_extraction,bodypart_analysis,text_classification ,text_extraction, labreport_extraction,output,history))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error inserting data into database: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    st.title("Image Testing Pipeline")

    # File uploader
    uploaded_file = st.file_uploader("Upload Image : ", type=["jpg", "jpeg", "png"])

    with st.container():
        c1,c2= st.columns([2,1])
        with c1 :
            if uploaded_file is not None:
                st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

        with c2 :
            if uploaded_file is not None:
                # Input fields for classification, text extraction, and response
                attachment_options = ['Nutrition', 'Body Part', 'Prescription', 'Medical Scan', 'Blood Report', 'Lab Report','Medically Relevant','<medical name for report> Report', 'other']
                attachment_type = st.selectbox("Type:", attachment_options)

                st.write("processing steps")

                if attachment_type=="Nutrition":
                    visual_classification= st.text_area("Visual Classification :")
                    nutrition_extraction = st.text_area("Nutrition Extraction :")
                    
                    output = st.text_input("Response:")
                    history = st.text_input("History: ")
                    text_extraction = ''
                    text_classification = ''
                    labreport_extraction =  ''
                    bodypart_analysis =''

                elif attachment_type=="Body Part":
                    visual_classification= st.text_area("Visual Classification")
                    bodypart_analysis = st.text_area("Body Part Analysis :")
                    output = st.text_input("Response:")
                    history = st.text_input("History: ")
                    text_extraction = ''
                    text_classification = ''
                    labreport_extraction =  ''
                    nutrition_extraction =''

                elif attachment_type=="Lab Report":
                    visual_classification= st.text_area("Visual Classification")
                    text_extraction = st.text_area(" Text Extraction:")
                    text_classification = st.text_input(" Text Classification:")
                    labreport_extraction =  st.text_area("Lab Report Extraction:")
                    output = st.text_input("Response:")
                    history = st.text_input("History: ")
                    nutrition_extraction =''
                    bodypart_analysis = ''
                
                else :
                    visual_classification= st.text_area("Visual Classification")
                    text_extraction = st.text_area(" Text Extraction:")
                    text_classification = st.text_input(" Text Classification:")
                    output = st.text_input("Response:")
                    history = st.text_input("History: ")
                    labreport_extraction =''
                    nutrition_extraction =''
                    bodypart_analysis = ''


                # Button to submit data
                if st.button("Submit"):
                    file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{uploaded_file.name}"

                    if upload_to_s3(uploaded_file) and insert_into_db( file_url , attachment_type , visual_classification, nutrition_extraction,bodypart_analysis,text_classification ,text_extraction, labreport_extraction,output,history):
                        st.success("Data inserted successfully!")
                    else:
                        st.error("Failed to insert data.")

if __name__ == "__main__":
    main()
