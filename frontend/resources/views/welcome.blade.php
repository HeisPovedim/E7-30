<?php 

    if(isset($_POST['data'])){
        dd($_POST['data']);
    }


?>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E7 - 30</title>
</head>
<style>
   html{
height: 100%;
background-color: seashell;
}
/* кнопка начало */

 .btn_back{
  width:90px;
  float: right;
  display:block;
  font-family: arial;
  text-decoration: none;
  font-weight: 300;
  font-size: 14px;
  border: #1071FF 1px solid;
  color: #1071FF;
  padding: 3px;
  padding-left: 5px;
  padding-right: 5px;
   margin: 20px auto;
  transition: .5s;
  border-radius: 0px;
}
.btn_back:hover {
  top: 5px;
  transition: .5s;
  color: red;
  border: red 1px solid;
  border-radius: 10px;
}
.btn_back:active {
  color: #000;
  border: #1A1A1A 1px solid;
  transition: .07s;
  background-color: #FFF;
}
/* кнопка конец */
body {
font-family: "Open Sans";
display: flex;
flex-direction: column;
height: 100%;
padding: 0;
margin: 0;

}

/* Настройка положения блоков */
header {
flex: 0 0 auto;
background-color: dodgerblue;
text-align: center;
color: white;
/*Шрифт */
font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
direction:ltr;
font-size: large;
}

main{
flex: 1 0 auto;
padding: 20px 20px 20px 20px;
background-color: seashell;
}
.conteiner{
    display: flex;
flex-direction: column;
}
footer {
text-align: center;
flex: 0 0 auto;
color: white;
background-color: dodgerblue;
/*Шрифт */
font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
direction:ltr;
font-size: large;
}
</style>
<body>
<header>
    <p>header</p>
</header>
        <main >
            <button class="btn_back" id='getData'>get data</button>
                <div class="conteiner">
                    <form action="/getData" method="post">
                    @csrf
                    <input type="number" name="f_start" placeholder="f_start" required />
                    <input type="number" name="f_end" placeholder="f_end" required/>
                    <input type="number" name="step" placeholder="step" required/><br>
                    <label for="z_only">z_only</label>
                    <input type="checkbox" name="z_only" placeholder="z_only" />
                    <input type="submit">
                    </form>
                </div>
        </main>
<footer>
    <p>Footer</p>
</footer>
</body>
<script type="text/javascript">

    //редирект
    document.getElementById("getData").onclick = function () {
        window.location.href = "/getData";
    };
</script>
</html>