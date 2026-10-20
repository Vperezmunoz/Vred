# Interact with webengines (calculator demo)
# source: VR-hands-webengine.html

calculatorNode = findNode("Calculator")
setNodeInteractableInVR(calculatorNode, True)

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="author" content="Pascal Seifert">
<style>
    *{
    box-sizing:  border-box;
    font-family: sans-serif;
    user-select:  none;
    -webkit-user-select: none;
}

  body{
  background-color: #000;
  font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;
  font-size: 36px;
}

main{
  position: absolute;
  top: 0;
  left: 0;
  width: 400px;
  height: 570px;
  display: flex;
  flex-direction: column;
}

#display{
  border: none;
  width: 100%;
  background-color: #000;
  font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;
  font-size: 72px;
  text-align: right;
  margin-right: 10px;
  color:  white;
}

main > div{
  flex: 5;
  display: flex;
  flex-direction: row;
}

main > div > div{
  flex: 4;
  display: flex;
  color: Black;
  text-align: center;
  border: 1px solid #000;
  justify-content: center;
  flex-flow: column wrap;
  background-color: #89a4c2;
}

main > div > div:hover{
  background-color: #7094bb;
}

main > div > div:active{
  transform:  scale(0.95);
}

.sign{
  background-color: #b9d39e;
  color: White;
}

.sign:hover{
  background-color: #a7cd8c;
  color: White;
}

.operator{
  background-color: #ff8000;
  color: White;
}

.operator:hover{
  background-color: #e0750a;
}
</style>

<title>HTML Calculator</title>
</head>
<body>
  <main>
    <div class="display"><input type="text" id="display" readonly>
    </div>
    <div>
      <div class="sign" value="AC" onmousedown='c("")'>AC</div>
      <div class="sign" value="(" onmousedown='math("(")'>(</div>
      <div class="sign" value=")" onmousedown='math(")")'>)</div>
      <div class="operator" onmousedown='math("/")'>&divide;</div>
    </div>
    <div>
      <div value="7" onmousedown='math("7")'>7</div>
      <div value="8" onmousedown='math("8")'>8</div>
      <div value="9" onmousedown='math("9")'>9</div>
      <div class="operator" onmousedown='math("*")'>&times;</div>
    </div>
    <div>
      <div value="4" onmousedown='math("4")'>4</div>
      <div value="5" onmousedown='math("5")'>5</div>
      <div value="6" onmousedown='math("6")'>6</div>
      <div class="operator" onmousedown='math("-")'>-</div>
    </div>
    <div>
      <div value="1" onmousedown='math("1")'>1</div>
      <div value="2" onmousedown='math("2")'>2</div>
      <div value="3" onmousedown='math("3")'>3</div>
      <div class="operator" onmousedown='math("+")'>+</div>
    </div>
    <div>
      <div value="" onmousemove='math("")'></div>
      <div value="0" onmousedown='math("0")'>0</div>
      <div value="," onmousedown='math(".")'>,</div>
      <div class="operator" onmousedown='e()'>=</div>
    </div>
  </main>

<script>function c(val){
  document.getElementById("display").value=val;
}

function math(val){
  document.getElementById("display").value+=val;
}

function e(){
  try{
   c(eval(document.getElementById("display").value));
  }
  catch(e){
   c('Error');
  }
}
</script>
</body>
