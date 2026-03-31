#import datetime

from datetime import datetime, timezone
from groq import Groq
from fastapi import FastAPI
####  from networkx import config
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from bson import ObjectId
from contextlib import asynccontextmanager
from mem0 import Memory
import json
import httpx
import asyncio         
from functools import partial

load_dotenv()


# memory = Memory.from_config({
#     "vector_store": {
#         "provider": "chroma", 
#         "config": {
#             "collection_name": "student_memory",
#             "path": "./mem0_db"
#         }
#     }
# })

memory = Memory.from_config({
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "student_memory",
            "path": "./mem0_db"
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2"
        }
    },
    "llm": {
        "provider": "groq",
        "config": {
            "model": "llama-3.3-70b-versatile",
            "api_key": os.getenv("GROQ_API_KEY")
        }
    }
})




ACTIVEPIECES_WEBHOOK_URL = os.getenv("ACTIVEPIECES_WEBHOOK_URL")



### menuu for groq to send arrangement of meeting (via email) using activepieces webhook

tools = [
    {
        "type" : "function",
        "function" : {
            "name" :  "arrange_meeting",
            "description" : "Schedule a meeting and nofify all students via email",
            "parameters" : {
                "type" : "object",
                "properties": {
                    "meeting_date": {
                        "type": "string",
                        "description": "Date of the meeting e.g. Monday April 7 2026"
                    },
                    "meeting_time": {
                        "type": "string",
                        "description": "Time of the meeting e.g. 10:00 AM"
                    },
                    "meeting_topic": {
                        "type": "string",
                        "description": "Topic or subject of the meeting"
                    },
                    "email_body": {
                        "type": "string",
                        "description": "A professional, nicely formatted HTML email body to send to all students about this meeting. Include date, time, topic, and a polite message."
                    }
                },
                "required": ["meeting_date", "meeting_time", "meeting_topic", "email_body"]
            }
        }
    }
]

async def notify_via_activepieces(subject: str, email_body: str, meeting_date: str, meeting_time: str, meeting_topic: str):
    students = await db.students.find({}, {"email": 1, "name": 1}).to_list(length=None)
    sent = 0
    async with httpx.AsyncClient() as http:
            for student in students:
                email = student.get("email")
                if not email:
                    continue
                await http.post(ACTIVEPIECES_WEBHOOK_URL, json={
                    "email": email,
                    "name": student.get("name"),
                    "subject": subject,
                    "email_body": email_body,
                    "meeting_date": meeting_date,
                    "meeting_topic": meeting_topic,
                    "meeting_time": meeting_time

                })
                sent +=1
    return sent


## RAG dependency
from rag_setup import retrieve, load_all_docs


# app = FastAPI()



@asynccontextmanager
async def lifespan(app: FastAPI):
    load_all_docs()  # ------ runs on startup of uviconcn
    yield            # server runs whne 
    
app = FastAPI(lifespan=lifespan)

# app.on_event("startup")
# async def startup_event():
#     load_all_docs()  ### this will load all the docs into vector once servereere starts...

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


        STRICT RULE: Only answer using the course material provided below.
        If the answer is not in the material, say "I don't have that information in my our database documents." and help them with general advice based on the course materials. Do NOT make up any information. If the question is not relevant to academics or course materials, politely decline to answer and suggest they ask something related to their studies. 
        Do NOT make up units, documents, or any information not explicitly given to you,act as us not them take the university resources as your knowledge base and answer based on that. Always try to relate the answer to the course materials and university resources.
        
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

        relevant_docs = retrieve(query.message)
        if relevant_docs:
            context += f"\n\n Relevant university resources:\n{relevant_docs}"

        mem0_results = await asyncio.get_running_loop().run_in_executor(
        None,
        partial(memory.search, query.message, user_id=query.student_id)
    )
    if mem0_results and mem0_results.get("results"):
        memory_text = "\n".join([m["memory"] for m in mem0_results["results"]])
        context += f"\n\nWhat you already know about this student from past conversations:\n{memory_text}\nUse this to personalize your response. Do not ask things you already know."


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

        await asyncio.get_running_loop().run_in_executor(
            None,
            partial(
                memory.add,
                messages=[
                    {"role": "user", "content": query.message},
                    {"role": "assistant", "content": ai_output}
                ],
                user_id=query.student_id
            )
        )
        
        if not ai_output:
            ai_output = "I couldn't generate a response., idk, things might be wrong"

        return {"reply": ai_output}
            
    except Exception as e:
        return {"reply": f"API Error: {str(e)}"}

        # return {"reply": ai_output

class TeacherChatRequest(BaseModel):
    message: str
    teacher_id: str
    mode : str = "chat"
    
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
          You are helping a teacher analyze their students performance if.

          teacher name is {teacher_doc.get('name', 'Unknown')}

          Each item contains:
         - student name
         - enrollment
         - result (CGPA, percentage, subjects, etc.)

        Analyze the full dataset and answer the teacher if the teacher asks.

         DATA:
          {merged_data}
          """
    # ai_output = "Something went wrong i guess, check line 285 to 300 in chatbot.py."

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

        is_meeting_request = any(word in query.message.lower() for word in ["meeting", "mail", "email", "schedule", "notify"])
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {"role": "system", "content": context},
                *teacherChat_history,
                {"role": "user", "content": query.message}
            ],
                tools=tools if query.mode == "schedule" or is_meeting_request else None,
                tool_choice="auto" if query.mode == "schedule" or is_meeting_request else "none"
        )
        ai_message = response.choices[0].message

        if ai_message.tool_calls:
            tool_call = ai_message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)

            if tool_call.function.name == "arrange_meeting":
                count = await notify_via_activepieces(
                    subject=f"📅 Meeting: {args['meeting_topic']} on {args['meeting_date']}",
                    email_body=args.get("email_body"),
                    meeting_date=args.get("meeting_date"),
                    meeting_time=args.get("meeting_time"),
                    meeting_topic=args.get("meeting_topic")
                )
                ai_output = f"✅ Done! Meeting scheduled for **{args['meeting_date']}** at **{args['meeting_time']}**. Notified **{count} students** via email."
            else:
                ai_output = "I tried to use a tool, but I don't know that why it didnt work, ask veer."
        else:
            ai_output = ai_message.content

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