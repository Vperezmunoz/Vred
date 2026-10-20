# Webengine menu demo
# source: menu-webengine.html

setNodeInteractableInVR(findNode("CurvedDisplay"), True)

<!DOCTYPE html>
<html>
<head>
    <meta content="text/html; charset=UTF-8">
    <meta name="author" content="Pascal Seifert">
    <title>Display</title>
    <link rel="stylesheet" type="text/css" href="main.css"/>
    <script type="text/javascript" src="script.js"></script>
</head>
<body>
    <div id="displaycolor">My Display</div>
</body>
</html>

<!DOCTYPE html>
<html>
<head>
    <meta content="text/html; charset=UTF-8">
    <meta name="author" content="Pascal Seifert">
    <title>Materials</title>
    <link id="light-style" rel="stylesheet" type="text/css" href="light.css"/>
    <link id="dark-style" rel="stylesheet" type="text/css" href="main.css"/>
    <script type="text/javascript" src="script.js"></script>
</head>
<body>
    <div class="menu">
        <div class="toolbar">
            <div class="header">Stylesheet</div>
            <div class="switch">
                <div id="checkbox-left" onclick="fn12()">
                    <div id="circle-left"></div>
                </div>
                <div id="checkbox-right" onclick="fn11()">
                    <div id="circle-right"></div>
                </div>
            </div>
        </div>
        <div class="toolbar">
            <div class="header">Tools</div>
            <div class="button" onclick="cl1()">
                <svg class="icon1"/>Wire
            </div>
            <div class="button" onclick="cl2()">
                <svg class="icon2"/>Clipping
            </div> 
            <div class="button" onclick="cl3()">
                <svg class="icon3"/>Ruler
            </div> 
            <div class="button" onclick="cl4()">
                <svg class="icon4"/>RayT.
            </div>
        </div>
        <div class="toolbar">
            <div class="header">Color</div>
            <div class="button" onclick="cl5()">
                <img class="png" src="assets/MatPink.png"/>Pink
            </div>
            <div class="button" onclick="cl6()">
                <img class="png" src="assets/MatBlue.png"/>Blue
            </div> 
            <div class="button" onclick="cl7()">
                <img class="png" src="assets/MatGreen.png"/>Green
            </div> 
            <div class="button" onclick="cl8()">
                <img class="png" src="assets/MatYellow.png"/>Yellow
            </div>
        </div>
        <div class="toolbar">
            <div class="header">Screen</div>
            <div class="button" onclick="cl9()">
                <img class="png" src="assets/BlackScreen.png"/>Black
            </div>
            <div class="button" onclick="cl10()">
                <img class="png" src="assets/WhiteScreen.png"/>White
            </div> 
        </div>
    </div>
</body>
</html>

/* Receive python commands from VRED */

/*
function setInnerHtml(id, html) {
  const e = document.getElementById(id);
  if (e) {
    e.innerHTML = html;
    return true;
  }
  return false;
}
*/


/* Tools Functions */
/* Wire Toggle */

function cl1() {
    vred.executePython("setWireframe(SWITCH_TOGGLE)");
    // example how to call a python command with a return value.
    //vred.executePythonCommand("getFov()", function(value) {
    //    window.alert(value);
    //});
};

/* Clipping Toggle */

var cl2 = (function() {
    var first = true;
    return function() {
        first ? fn1() : fn2();
        first = !first;
    }
})();

function fn1(){
  vred.executePython("enableClippingPlane(true)");
};

function fn2(){
  vred.executePython("enableClippingPlane(false)");
};

/* Ruler Toggle */

var cl3 = (function() {
    var first = true;
    return function() {
        first ? fn3() : fn4();
        first = !first;
    }
})();

function fn3(){
  vred.executePython("showRuler(true)");
};

function fn4(){
  vred.executePython("showRuler(false)");
};

/* Ray Toggle */

var cl4 = (function() {
    var first = true;
    return function() {
        first ? fn5() : fn6();
        first = !first;
    }
})();

function fn5(){
  vred.executePython("toggleRaytracing(true)");
};

function fn6(){
  vred.executePython("toggleRaytracing(false)");
};


/* Materials Functions */
/* Switch Material Color */

function cl5() {
  vred.executePython("value=setSwitchMaterialChoice('SwitchMaterial', 0)");
};

function cl6() {
  vred.executePython("value=setSwitchMaterialChoice('SwitchMaterial', 1)");
};

function cl7() {
  vred.executePython("value=setSwitchMaterialChoice('SwitchMaterial', 2)");
};

function cl8() {
  vred.executePython("value=setSwitchMaterialChoice('SwitchMaterial', 3)");
};


/* DisplayUI Functions */
/* Screen Color */

function cl9(){
        vred.executePython("vrWebEngineService.getWebEngine('WebEngine_Display').sendEvent('Color1', '')");
};

function cl10(){
        vred.executePython("sendToWebEngine('WebEngine_Display', 'Color2', '')");
};

/* Display EventListener´s Function*/

changecolor1 = function(event){
    
    var fieldNameElement = document.getElementById("displaycolor");
            fieldNameElement.style.backgroundColor = '#000000';
            fieldNameElement.textContent = "Black Screen";   
};

document.addEventListener("Color1", changecolor1);

changecolor2 = function(event){
    
        var fieldNameElement = document.getElementById("displaycolor");
            fieldNameElement.style.backgroundColor = '#FFFFFF';
            fieldNameElement.textContent = "White Screen";
};

document.addEventListener("Color2", changecolor2);

/*Switch*/

changestyle1 = function(event){
    
            document.getElementById("dark-style").disabled = true;
            document.getElementById("light-style").disabled = false;
};

document.addEventListener("Style1", changestyle1);

function fn11(){
    
            document.getElementById("dark-style").disabled = true;
            document.getElementById("light-style").disabled = false;
            vred.executePython("vrWebEngineService.getWebEngine('WebEngine_Tools').sendEvent('Style1', '')");
};

changestyle2 = function(event){
    
            document.getElementById("dark-style").disabled = false;
            document.getElementById("light-style").disabled = true;
};

document.addEventListener("Style2", changestyle2);

function fn12(){
    
            document.getElementById("dark-style").disabled = false;
            document.getElementById("light-style").disabled = true;
            vred.executePython("vrWebEngineService.getWebEngine('WebEngine_Tools').sendEvent('Style2', '')");
};
