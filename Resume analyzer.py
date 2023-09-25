import os
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from pdfminer.high_level import extract_text
import openai

# Set your OpenAI API key here
api_key = ""

job_description = """
Job Description:
We are seeking a talented Data Scientist to join our team. The ideal candidate will have a passion for uncovering insights from data and driving data-driven decision-making. As a Data Scientist, you will be responsible for developing and implementing innovative data analysis solutions to solve complex business problems. You will work closely with cross-functional teams to translate data into actionable insights and contribute to the development of data-driven strategies.

Key Responsibilities:

- Data Analysis: Analyze large datasets to identify trends, patterns, and correlations, and derive actionable insights.
- Machine Learning: Develop and implement machine learning models for predictive and prescriptive analytics.
- Data Visualization: Create visually compelling data visualizations and reports to communicate findings effectively.
- Statistical Analysis: Apply statistical methods to validate hypotheses and draw meaningful conclusions.
- Data Cleaning: Clean and preprocess raw data to ensure data quality and accuracy.
- Model Evaluation: Evaluate and fine-tune machine learning models for optimal performance.
- Cross-Functional Collaboration: Collaborate with teams across the organization to understand business objectives and provide data-driven solutions.
- Research: Stay updated with the latest industry trends and emerging technologies in data science.

Required Skills:

- Proficiency in programming languages such as Python or R.
- Strong knowledge of machine learning algorithms and techniques.
- Experience with data manipulation libraries (e.g., pandas, NumPy) and machine learning frameworks (e.g., scikit-learn, TensorFlow).
- Data visualization skills using tools like Matplotlib, Seaborn, or Tableau.
- Excellent problem-solving and analytical skills.
- Effective communication skills to convey complex findings to non-technical stakeholders.
- Knowledge of statistical analysis and hypothesis testing.
- Familiarity with databases and SQL.
- Experience with big data technologies (e.g., Hadoop, Spark) is a plus.

Experience:

- Bachelor's, Master's, or Ph.D. in a relevant field (e.g., Computer Science, Statistics, Mathematics).
- Minimum of 3 years of experience as a Data Scientist or in a similar role.
- Proven track record of successfully applying data science techniques to solve real-world problems.
- Experience in working with large-scale datasets and machine learning model development.

Join our team and play a crucial role in driving data-driven decision-making, innovation, and growth within our organization. If you are passionate about data and have the skills to make a significant impact, we would love to hear from you.
"""

def analyze_resume(user_resume, job_description, api_key):
    openai.api_key = api_key

    system_msg = 'You are a helpful assistant who understands the contents of a resume and a job description given by the user.'

    job_insights = []

    # Construct the prompt with user's resume and job description
    prompt = f"{system_msg}\nUser Resume:\n{user_resume}\n\nJob Description:\n{job_description}\n\nPlease analyze the user's resume and compare it to the job description. Focus on academic qualifications, skills, work experience, and projects. Highlight strengths and weaknesses for the specific job role and suggest skills to improve:\n\nStrengths:\n- Compare the skills, projects and degree to that with job description and mention the matching skills/degrees as strengths.\n- If experience section is present, see how the experience is relevant to the job description.\n- Notable projects completed, including [mention projects] if they are relevant to the job description.\n\nWeaknesses:\n- If the resume has a different degree than what is mentioned in the job description.\n- Projects could benefit from more [mention improvements].\n\nSuggested Improvements:\n- Enhance skills in [mention skills] through courses, certification or projects that will help show-off your skills.\n- Seek opportunities to gain more experience in [mention area].\n\nOverall, the candidate is suitable for the job but needs to improve on [specify the skills] or if the job description and resume has more than 5 differences, the user's resume does not match the job."

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    job_insight = response["choices"][-1]["message"]["content"]
    job_insights.append(job_insight)

    return job_insights

def on_drop(event):
    file_path = event.data
    if file_path.lower().endswith('.pdf'):
        process_pdf(file_path)
    else:
        print("Please drop a PDF file.")

def process_pdf(pdf_file_path):
    pdf_text = extract_text(pdf_file_path)
    analysis = analyze_resume(pdf_text, sample_job_description, api_key)
    print(analysis)

# Create a root window for the GUI
root = TkinterDnD.Tk()
root.title("PDF File Drag and Drop")

# Create a label for instructions
instructions_label = tk.Label(root, text="Drag and drop a PDF file here")
instructions_label.pack(pady=20)

# Create a drop target
drop_target = tk.Label(root, text="Drop Here", bg="lightgray", width=40, height=10)
drop_target.pack()

# Bind the drop event to the on_drop function
drop_target.drop_target_register(DND_FILES)
drop_target.dnd_bind('<<Drop>>', on_drop)

# Start the GUI main loop
root.mainloop()