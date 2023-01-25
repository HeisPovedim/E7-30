import express from 'express';
import { PythonShell } from 'python-shell';
import shell from 'shelljs';
import cors from 'cors';

import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const fs = require('fs');

const app = express();
app.use(express.json());
app.use(cors());

// ?: Конфигруация
let PORT = process.env.PORT || 3456;

app.listen(PORT, () => {
  console.log('server is running to port: ' + PORT);
});

let z_only = {
  with_Z: ['F =, ', 'Z =, ', 'Phi = ,'],
  without_Z: ['F =, ', 'Gp =, ', 'Rp =, ', 'Cp =, ', 'F =, ', 'Z =, ', 'Phi =, ']
}
app.post("/start", async (req, res) => {
  const param = req.body; 
  console.log(param);

  // редактирование файла launch.sh
  const filePath = 'launch.sh';
  const fileContent = `#!/bin/sh\n\npython3 pool.py ${param["f_start"]} ${param["f_end"]} ${param["step"]} test.csv no-report ${(param["z_only"])?'z-only':''} `;
  var promise = new Promise((resolve,reject)=>{
    //редактирование файла
    fs.writeFile(filePath, fileContent, (err) => {
      if (err) {
        console.error(err);
        throw new Error(err);
      }
      resolve('good');
    });
  });
  promise.then(()=>{
      //запуск скрипта
    shell.exec('sh launch.sh', (error, stdout, stderr) => {
      stdout = stdout.substring(0, stdout.length - 1).split('\n');
      const stdoutLength = Object.keys(stdout).length;
      for (let i = 0; stdoutLength > i; i++) {
        stdout[i] = stdout[i].substring(0, stdout[i].length - 1).substring(1); // удаление мусора в объектах
        if (param.z_only == true) {
          stdout[i] = `${z_only.with_Z[i]}` + stdout[i];
        } else { stdout[i] = `${z_only.without_Z[i]}` + stdout[i] }
      }
      res.send(stdout);
    })
  })
  
})

app.post("/1", (req, res) => {
  //пришли параметры с фронта
  const param = req.body; 
  console.log(param);
 


  //редактирование файла launch.sh
  const filePath = 'launch.sh';
  const fileContent = `#!/bin/sh\n\npython3 pool.py ${param["f_start"]} ${param["f_end"]} ${param["step"]} test.csv no-report ${(param["z_only"])?'z_only':''} `;

  fs.writeFile(filePath, fileContent, (err) => {
    if (err) {
      console.error(err);
      return;
    }
    console.log(`The file was saved at ${filePath}`);
  });
  res.sendStatus(200);
})



