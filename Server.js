const dotenv = require('dotenv');
dotenv.config();
const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const morgan = require('morgan');

const connectDB = require('./server/database/connectDB');
connectDB();
const app = express();

app.use(express.json());  // this thing destroyed my whole day
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(morgan('dev'));
app.set('view engine', 'ejs');

app.use('/', require('./server/routes/route'))

app.listen(process.env.PORT, () => {
    console.log(`Server is running on port ${process.env.PORT}`);
})
