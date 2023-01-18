import express from 'express';
import { PythonShell } from 'python-shell';
import shell from 'shelljs';
import cors from 'cors';

const app = express();
app.use(express.json());
app.use(cors());

// ?: Конфигруация
let PORT = process.env.PORT || 3456;

app.listen(PORT, () => {
  console.log('server is running to port: ' + PORT);
});

app.get("/start", (req, res) => {
  shell.exec('sh launch.sh', (error, stdout, stderr) => {
    console.log( stdout);
    res.send(stdout);
  })
})