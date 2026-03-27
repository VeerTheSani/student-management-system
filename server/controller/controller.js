const dotenv = require('dotenv');
dotenv.config();
const Student = require('../model/student');
const Teacher = require('../model/teacher');
const Result = require('../model/result')
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const salt = 12;
const axios = require('axios');

exports.login = async (req, res) => {
    const { email, password, role } = req.body;
    console.log("ROLE:", role)
    if (!email || !password) {
        return res.status(401).json({ msg: "all fiels are required" });
    }
    if (role == 'student') {
        const student = await Student.findOne({ email: email });
        try {
            if (!student) {
                return res.status(401).json({ messgae: "student not found" });
            }
            const isMatch = await bcrypt.compare(password, student.password);
            if (!isMatch) {
                return res.status(402).json({ message: "invalid credencials" });
            }
            console.log(isMatch);
            const token = jwt.sign({
                role: student.role,
                email: student.email,
            }, process.env.JWT_SECRET, { expiresIn: "1h" })
            console.log(token)
            res.cookie("token", token, { httpOnly: true });
            console.log(res.cookie)
            res.redirect('/Sdashboard');
        } catch (error) {
            return res.status(400).json({ error: error.message });
            console.log(error)
        }
    }

    else if (role == 'teacher') {
        try {
            const teacher = await Teacher.findOne({ email: email });
            console.log(teacher);
            if (!teacher) {
                return res.status(401).json({ messgae: "teacher not found" });
            }
            const isMatch = await bcrypt.compare(password, teacher.password);
            if (!isMatch) {
                return res.status(402).json({ message: "invalid credencials" });
            }
            console.log(isMatch);

            const token = jwt.sign({
                role: teacher.role,
                email: teacher.email,

            }, process.env.JWT_SECRET, { expiresIn: "1h" })
            console.log(token);
            res.cookie("token", token, { httpOnly: true });
            console.log(res.cookie)
            res.redirect("/Tdashboard");
        } catch (error) {
            return res.status(400).json({ error: error.message });
            console.log(error)
        }

    }

    else {
        res.send({ error: "role not find" })
    }
}

exports.registerS = async (req, res) => {
    const { email, enroll, name } = req.body;
    let password = req.body.password;

    if (!email || !enroll || !name || !password) {
        return res.status(402).json({ message: "all fields are required" });
    }
    try {
        const existUser = await Student.findOne({ email: email });
        console.log(email, enroll, name);
        if (existUser) {
            return res.status(402).json({ message: "User alredy existed" });
        }
        const hashpass = await bcrypt.hash(password, salt);
        console.log(hashpass)
        password = hashpass

        const student = await Student.create({ email, name, enroll, password });
        console.log(student)
        const token = jwt.sign({
            email: student.email,
            role: "student"
        },
            process.env.JWT_SECRET,
            { expiresIn: "1h" });
        res.cookie("token", token, { httpOnly: true });
        res.redirect('/Sdashboard');
    } catch (error) {
        return res.status(400).json({ error: error.message });
        console.log(error)
    }
}

exports.registerT = async (req, res) => {
    const { email, t_id, name } = req.body;
    let password = req.body.password;
    if (!email || !t_id || !name || !password) {
        return res.status(402).json({ message: "all fields are required" });
    }
    try {
        const existUser = await Teacher.findOne({ email: email });
        if (existUser) {
            return res.status(402).json({ message: "User alredy existed" });
        }

        const hashpass = await bcrypt.hash(password, salt);
        password = hashpass

        const teacher = await Teacher.create({ email, name, t_id, password });
        console.log(teacher)
        const token = jwt.sign({
            email: teacher.email,
            role: "teacher"
        },
            process.env.JWT_SECRET,
            { expiresIn: "1h" });
        res.cookie("token", token, { httpOnly: true });
        res.redirect('/Tdashboard');
    } catch (error) {
        return res.status(400).json({ error: error.message });
        console.log(error)
    }
}

exports.getProfile = async (req, res) => {
    const email = req.user.email;
    try {

        const student = await Student.findOne({ email: email });

        const result = await Result.findOne({
            studentId: student._id,
            sem: 1
        });

        if (!student) {
            return res.status(401).json({ message: "student not found" });
        }
        res.render('./student/Sprofile', { student, result })
    }
    catch (error) {
        return res.status(400).json({ error: error.message });
        console.log(error)
    }
}

exports.getTProfile = async (req, res) => {
    const email = req.user.email;
    try {
        const teacher = await Teacher.findOne({ email: email });
        if (!teacher) {
            return res.status(401).json({ message: "teacher not found" });
        }
        res.render('./teacher/Tprofile', { teacher })
    }
    catch (error) {
        return res.status(400).json({ error: error.message });
        console.log(error)
    }
}

exports.Sdashboard = async (req, res) => {
    const email = req.user.email;
    try {
        const student = await Student.findOne({ email: email });

        const results = await Result.find({
            studentId: student._id
        }).sort({ sem: 1 });

        if (!student) {
            return res.status(401).json({ message: "student not found" });
        }
        res.render("./student/Sdashboard", {
            student,
            results
        });
    }
    catch (error) {
        return res.status(400).json({ error: error.message });
        console.log(error)
    }
}

exports.Tdashboard = async (req, res) => {
    const email = req.user.email;
    try {
        const teacher = await Teacher.findOne({ email: email });
        if (!teacher) {
            return res.status(401).json({ message: "Teacher not found" });
        }

        const totalStudents = await Student.countDocuments()

        const totalResults = await Result.countDocuments()

        const passCount = await Result.countDocuments({ resultStatus: "Pass" })
        const failCount = await Result.countDocuments({ resultStatus: "Fail" })

        const passPercentage = ((passCount / totalStudents) * 100).toFixed(2)

        const topStudent = await Result.findOne().sort({ CGPA: -1 })
        const results = await Result.find();

        const students = await Student.aggregate([
            {
                $lookup: {                           // join student collection with results collection
                    from: "results",
                    localField: "_id",
                    foreignField: "studentId",
                    as: "result"
                }
            },
            {
                $unwind: {                        // convert array to object
                    path: "$result",
                    preserveNullAndEmptyArrays: true
                }
            },
            {
                $project: {                    //from whole colle tion it return only needed data
                    name: 1,
                    enroll: 1,
                    sem: "$result.sem",
                    CGPA: "$result.CGPA",
                    resultStatus: "$result.resultStatus"
                }
            }
        ]);
        const subjectMap = {};

        results.forEach(r => {
            r.subjects.forEach(sub => {

                if (!subjectMap[sub.subject]) {
                    subjectMap[sub.subject] = { total: 0, count: 0 };
                }

                subjectMap[sub.subject].total += sub.marks;
                subjectMap[sub.subject].count += 1;

            });
        });

        const performanceData = Object.keys(subjectMap).map(subject => ({
            subject,
            avgMarks: subjectMap[subject].total / subjectMap[subject].count
        }));

        res.render("./teacher/Tdashboard", {
            students,
            teacher,
            totalStudents,
            totalResults,
            passPercentage,
            topCGPA: topStudent?.CGPA || 0,
            passCount,
            failCount,
            performanceData
        })
    }
    catch (error) {
        return res.status(400).json({ error: error.message });
        console.log(error)
    }
}

exports.getResults = async (req, res) => {

    const student = await Student.findOne({
        email: req.user.email
    });

    const result = await Result.findOne({
        studentId: student._id,
        sem: 1
    });

    if (!result) {
        return res.send("Result not uploaded yet");
    }

    res.render("./student/Sresult", { result, student });
};

// --------------for csv file processing
const fs = require("fs");
const csv = require("csv-parser");


// exports.uploadResults = async (req, res) => {

//     if (!req.file) {
//         return res.status(400).send("No CSV file uploaded");
//     }
//     console.log("Uploaded file:", req.file);
//     const rows = [];

//     fs.createReadStream(req.file.path)
//         .pipe(csv())
//         .on("data", (row) => {
//             rows.push(row);
//         })

//         // .on("end", async () => {

//         //     for (let data of rows) {

//         //         const student = await Student.findOne({
//         //             enroll: data.enroll
//         //         });

//         //         if (!student) continue;

//         //         let result = await Result.findOne({
//         //             studentId: student._id,
//         //             sem: data.sem
//         //         });

//         //         if (!result) {
//         //             result = new Result({
//         //                 studentId: student._id,
//         //                 sem: data.sem,
//         //                 subjects: []
//         //             });
//         //         }

//         //         result.subjects.push({
//         //             subject: data.subject,
//         //             marks: Number(data.marks)
//         //         });

//         //         await result.save();
//         //     }

//         //     fs.unlinkSync(req.file.path);

//         //     res.send("CSV Uploaded Successfully");
//         // });
//         .on("end", async () => {

//             for (let data of rows) {

//                 console.log("CSV enroll:", data.enroll);

//                 const student = await Student.findOne({
//                     enroll: data.enroll.trim()
//                 });

//                 console.log("Student found:", student);
//                 console.log("CSV enroll:", data.enroll);
//                 if (!student) {
//                     console.log("Student not found, skipping");
//                     continue;
//                 }

//                 console.log("Student found:", student);

//                 let result = await Result.findOne({
//                     studentId: student._id,
//                     sem: data.sem
//                 });


//                 if (!result) {
//                     result = new Result({
//                         studentId: student._id,
//                         sem: data.sem,
//                         subjects: []
//                     });
//                 }

//                 result.subjects.push({
//                     subject: data.subject,
//                     marks: Number(data.marks)
//                 });

//                 await result.save();
//             }

//             res.send("CSV Uploaded Successfully");

//         });
// };
exports.uploadResults = async (req, res) => {
    if (!req.file) {
        return res.status(400).send("No CSV file uploaded");
    }

    const rows = [];

    fs.createReadStream(req.file.path)
        .pipe(csv())
        .on("data", (row) => {
            rows.push(row);
        })
        .on("end", async () => {
            for (let data of rows) {

                console.log("Row:", data); // DEBUG

                const student = await Student.findOne({
                    enroll: data.enroll   // FIX THIS if needed
                });

                if (!student) {
                    console.log("Student not found:", data.enroll);
                    continue;
                }

                let result = await Result.findOne({
                    studentId: student._id,
                    sem: data.sem
                });

                if (!result) {
                    result = new Result({
                        studentId: student._id,
                        sem: data.sem,
                        subjects: []
                    });
                }

                const existingSubject = result.subjects.find(
                    s => s.subject === data.subject
                );

                if (existingSubject) {
                    existingSubject.marks = Number(data.marks);
                } else {
                    result.subjects.push({
                        subject: data.subject,
                        marks: Number(data.marks)
                    });
                }

                const totalMarks = result.subjects.reduce((sum, s) => sum + s.marks, 0);
                const maxMarks = result.subjects.length * 100;

                result.total = totalMarks;
                result.percentage = (totalMarks / maxMarks) * 100;
                result.CGPA = (result.percentage / 9.5).toFixed(2);
                result.creditsEarned = result.subjects.length * 4;

                const hasFail = result.subjects.some(sub => sub.marks < 40);
                result.resultStatus = hasFail ? "Fail" : "Pass";

                await result.save();
            }

            fs.unlinkSync(req.file.path);
            res.send("CSV Uploaded Successfully");
        });
};

exports.uploadStudent = async (req, res) => {

    if (!req.file) {
        return res.status(400).send("No CSV file uploaded");
    }

    const rows = [];

    fs.createReadStream(req.file.path)
        .pipe(csv())
        .on("data", (row) => {
            rows.push(row);
        })
        .on("end", async () => {
            for (let data of rows) {

                const email = data.email.trim();
                const name = data.name.trim();
                const enroll = data.enroll.trim();
                const student = await Student.create({
                    email,
                    name,
                    enroll,
                    password: await bcrypt.hash(data.password, salt)
                })

                existStudent = await Student.findOne({ enroll: data.enroll });

                if (!student) {
                    console.log("Student not found:", data.enroll);
                    continue;
                }
                if (existStudent) {
                    console.log("Student already exists:", data.enroll);
                    continue;
                }

            }
            fs.unlinkSync(req.file.path); // remove uploaded csv
            res.send("CSV Uploaded Successfully");
        });
};

// ## my code for chat with teacher and student
exports.chatt = async (req, res) => {
    try {
        const email = req.user.email
        const student = await Student.findOne({ email })

        const response = await axios.post('http://127.0.0.1:8000/chatt', {
            message: req.body.message,
            student_id: student._id.toString()
        })

        res.json({ reply: response.data.reply })
    } catch (error) {
        console.error("Error in chatt:", error);
        res.status(500).json({ error: "Backend connection failed. Check Node console" });
    }
}

exports.tchatt = async (req, res) => {
    try {
        const email = req.user.email
        const teacher = await Teacher.findOne({ email })

        const response = await axios.post('http://127.0.0.1:8000/tchatt', {
            message: req.body.message,
            teacher_id: teacher._id.toString()
        })

        res.json({ reply: response.data.reply })
    } catch (error) {
        console.error("Error in tchatt:", error);
        res.status(500).json({ error: "Backend connection failed. Check Node console" });
    }
}


// download pdf of reuslt
const PDFDocument = require("pdfkit");


exports.downloadResult = async (req, res) => {

    const studentId = req.params.id;

    const student = await Student.findById(studentId);
    const result = await Result.findOne({ studentId });

    if (!student || !result) {
        return res.send("Result not found");
    }

    const doc = new PDFDocument();

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader(
        "Content-Disposition",
        `attachment; filename=${student.enroll}_result.pdf`
    );

    doc.pipe(res);

    // Title
    doc.fontSize(20).text("Student Result Sheet", { align: "center" });
    doc.moveDown();

    // Student Info
    doc.fontSize(12).text(`Name: ${student.name}`);
    doc.text(`Enrollment: ${student.enroll}`);
    doc.text(`Semester: ${result.sem}`);
    doc.moveDown();

    // Subjects
    doc.text("Subjects:", { underline: true });
    doc.moveDown();

    result.subjects.forEach((s) => {
        doc.text(`${s.subject} : ${s.marks}`);
    });

    doc.moveDown();

    doc.text(`Total: ${result.total}`);
    doc.text(`Percentage: ${result.percentage.toFixed(2)}%`);
    doc.text(`CGPA: ${result.CGPA}`);
    doc.text(`Status: ${result.resultStatus}`);

    doc.end();
};