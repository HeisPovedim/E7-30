
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
  text-align: center;
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
            <form  method="post" action="/getData">
                @csrf
                <input type="number" required name='start_range' placeholder="Начальная частота">
                <input type="number" required name='end_range' placeholder="Конечная частота">
                <input type="number" required name='step' placeholder="Шаг">
                <button class="btn_back"  type="submit">save data</button>
            </form>
                <button class="btn_back" id='getData' >get data</button>

                <div class="conteiner" id='dataBlock'>
                    <?php
                    $respone = session()->get('data');
                    $data = explode("\r", $respone) ;
                    $datalenght = count($data);
                    unset($data[$datalenght-1]);
                    if(($data))
                    {
                        echo "<h1>- Получены данные ...</h1>";
                        date_default_timezone_set('Europe/Moscow');
                        $date = date('m/d/Y h:i:s a', time());
                        echo"<h2>Время получения данных - $date</h2>";
                        foreach ($data as &$el) {
                            echo "<p>- $el.</p>";
                        }
                        echo"<button class='btn_back' id='closeData'>close data</button>";
                    } 
                    ?>
                </div>
        </main>
<footer>
    <p>Footer</p>
</footer>
</body>

<script type="text/javascript">
    //logic
    if(document.getElementById('closeData')){
        document.getElementById('getData').style.display='none';
    }

    //start
/*     document.getElementById("getData").onclick = function () {
        window.location.href = "/getData";
    } */
    //end
/*     document.getElementById("closeData").onclick= function(){
        document.getElementById('dataBlock').remove();
        document.getElementById('getData').style.display='';
        } */

</script>
</html>