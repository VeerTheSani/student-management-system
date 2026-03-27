#import datetime

from datetime import datetime, timezone
from groq import Groq
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    student_id: str
    

mongo = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = mongo["student_mgm2"]

@app.post("/chatt")
async def chat_userquery(query: ChatRequest):
    
    student_doc = await db.students.find_one({"_id": ObjectId(query.student_id)})
    # result_doc = await db.results.find_one({"student_id": ObjectId(query.student_id)})
    result_doc = await db.results.find_one({"studentId": ObjectId(query.student_id)})
    try:
        if not student_doc:
            return {"reply": "Student not found."}
    except Exception as e:
        return {"reply": f"Error occurred: {str(e)}"}


    if not result_doc:
        result_doc = {}

    context = f"""
        You are an academic assistant built, help this following student:

        Student Name: {student_doc.get('name', 'Unknown')}
        Enrollment Number: {student_doc.get('enrollment', 'Unknown')}
        Email: {student_doc.get('email', 'Unknown')}

        the student's academics results are as follows:

        percentage :{result_doc.get('percentage', 'Unknown')}
        sem :{result_doc.get('sem', 'Unknown')}
        credits : {result_doc.get('creditsEarned', 'Unknown')}
        status : {result_doc.get('resultStatus', 'N/A')}
        CGPA : {result_doc.get('CGPA', 'Unknown')}

        Analyze their performance and give suggestions regarding where to improve (in brief and short).
        

        note : it student has no results yet, then just give general advice in brief as ai web assistant.
        now below the student will ask for the first time so greet and answer and assist like human tone.

        studnet chat history : 
        """
    history_docs = await db.students_history.find(
    {"student_id": ObjectId(query.student_id)}).sort("created_at", -1).limit(5).to_list(length=5)
    history_docs.reverse()  ### i am not sure why iam reversing because i am the reverserser right? what ??.there is no word like reverserser ,, wtf ? its onl reverse

    studentChatHistory = []

    

    for doc in history_docs:
        user_msges = doc.get("query")
        assistant_msges = doc.get("response")

        if not user_msges or not assistant_msges:
            continue

        studentChatHistory.append({"role": "user", "content": user_msges})
        studentChatHistory.append({"role": "assistant", "content": assistant_msges})
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {"role": "system", "content": context},
                *studentChatHistory,
                {"role": "user", "content": query.message}
            ]
        )
        ai_output = response.choices[0].message.content

        await db.students_history.insert_one({
            "student_id": ObjectId(query.student_id),
            "query": query.message,
            "response": ai_output,
            "created_at": datetime.now(timezone.utc)
        })
        
        if not ai_output:
            ai_output = "I couldn't generate a response., idk, things might be wrong"

        return {"reply": ai_output}
            
    except Exception as e:
        return {"reply": f"API Error: {str(e)}"}

        # return {"reply": ai_output

class TeacherChatRequest(BaseModel):
    message: str
    teacher_id: str
    
@app.post('/tchatt')
async def chat_teacherquery(query: TeacherChatRequest):
    students = await db.students.find().to_list(length=100)
    # result_doc = await db.results.find({"student_id": query.student_id})

    results = await db.results.find().to_list(length=100)
    teacher_doc = await db.teachers.find_one({"_id": ObjectId(query.teacher_id)})
    
    # ### avengers !! assmeble!!!!!!!
    student_map = {}

    for s in students:
            sid = str(s["_id"])
            student_map[sid] = {
                "name": s.get("name"),
                "enroll": s.get("enroll"),
                "result": None
            }

        
    for r in results:
            sid = str(r["studentId"])
            if sid in student_map:
                clean_result = {k: str(v) if isinstance(v, ObjectId) else v for k, v in r.items()}
                student_map[sid]["result"] = clean_result


    
    merged_data = list(student_map.values())

#      if_itworks_lmao = ""

#         for data in student_map.values():
#             r = data["result"]
#             if not r:
#                 continue

#             subjects = r.get("subjects", [])
#             subject_str = ", ".join(
#                 [f"{sub['subject']}:{sub['marks']}" for sub in subjects]
#             )

#             summary += f"""
# Name: {data['name']}
# CGPA: {r.get('CGPA')}
# Percentage: {r.get('percentage')}
# Subjects: {subject_str}

# """


    
    context = f"""
          You are an academic assistant built by student management system website( sms portal ).
          You are helping a teacher analyze their students performance.

          teacher name is {teacher_doc.get('name', 'Unknown')}

          Each item contains:
         - student name
         - enrollment
         - result (CGPA, percentage, subjects, etc.)

        Analyze the full dataset and answer the teacher.

         DATA:
          {merged_data}
          """
    ai_output = "Something went wrong."

    teacher_chat_history_docs = await db.teachers_history.find(
    {"teacher_id": ObjectId(query.teacher_id)}).sort("created_at", -1).limit(5).to_list(length=5)
    teacher_chat_history_docs.reverse()

    teacherChat_history = []

    for doc in teacher_chat_history_docs:
        teacher_msges = doc.get("query")
        assistant_msges = doc.get("response")

        if not teacher_msges or not assistant_msges:
            continue

        teacherChat_history.append({"role": "user", "content": teacher_msges})
        teacherChat_history.append({"role": "assistant", "content": assistant_msges})

        
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {"role": "system", "content": context},
                *teacherChat_history,
                {"role": "user", "content": query.message}
            ]
        )
        ai_output = response.choices[0].message.content

        await db.teachers_history.insert_one({
            "teacher_id": ObjectId(query.teacher_id),
            "query": query.message,
            "response": ai_output,
            "created_at": datetime.now(timezone.utc)
        })
        
        if not ai_output:
            ai_output = "I couldn't generate a response., the question is , are you sure your even a tacher?"
        
    except Exception as e:
        ai_output = f"API Error: {str(e)}"
        
    return {"reply": ai_output}