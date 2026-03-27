const express = require('express');
const router = express.Router();
const controller = require('../controller/controller')
const upload = require("../middleware/upload");

const verify = require('../middleware/verify');

router.get('/', (req, res) => {
    res.render('firstPage');
})

router.get('/student', (req, res) => {
    res.render('./student/studentRes');
})

router.get('/teacher', (req, res) => {
    res.render('./teacher/teacherRes');
})
router.get('/login', (req, res) => {
    res.render('login');
})
router.get('/home', verify, (req, res) => {
    res.render('home');
})


router.get('/Sprofile', verify, controller.getProfile)
router.get('/Sdashboard', verify, controller.Sdashboard)
router.get('/Sresult', verify, controller.getResults)

// teacher
router.get('/Tprofile', verify, controller.getTProfile)
router.get('/Tdashboard', verify, controller.Tdashboard)
router.get('/result', verify, (req, res) => {
    res.render('./teacher/result');
})

router.post('/login', controller.login);
router.post('/registerS', controller.registerS);
router.post('/registerT', controller.registerT);
router.post(
  "/uploadResults",
  upload.single("file"),   // FIRST
  verify,                  // SECOND
  controller.uploadResults
);

router.post(
  "/uploadStudent",
  upload.single("file"),   // FIRST
  verify,                  // SECOND
  controller.uploadStudent
);
router.get("/download-result/:id", controller.downloadResult);

router.post('/chatt', verify, controller.chatt);
router.post('/tchatt', verify, controller.tchatt);


module.exports = router;