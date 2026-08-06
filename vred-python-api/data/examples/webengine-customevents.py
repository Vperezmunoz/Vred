# Custom Javascript events in Webengines
# source: webengine-customevents.html

var e = new CustomEvent( event
     {
         detail: data
     });

 document.dispatchEvent(e);

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JavaScript Custom Event</title>
</head>
<body style="background-color:white;">
    <div class="note">JavaScript Custom Event</div>
    <script>
        document.addEventListener("testEvent", function(event) {
            document.body.style.background = event.detail.color;
        });
    </script>
</body>
</html>

we = vrWebEngineService.getWebEngine("EventFrontPlate")

we.sendEvent("testEvent", "{color: 'red'}")

we.sendEvent("testEvent", "{color: 'green'}")

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JavaScript Custom Event</title>
</head>
<body style="background-color:white;">
    <div class="note">JavaScript Custom Event</div>
    <script>
        document.addEventListener("testEvent", function(event) {
            vred.executePython("printFromJavascript('" + event.detail.custom + "')");
        });
    </script>
</body>
</html>

def printFromJavascript(data):
  print(data)

we = vrWebEngineService.getWebEngine("EventFrontPlate")
we.sendEvent("testEvent", "{custom: 'test 123'}")

<script>
var e = new CustomEvent("testEvent"
        {
          detail: {custom: 'test 123' }
        });
</script>

sendToWebEngine(name, event, data)

sendToWebEngine("EventFrontPlate", "testEvent", "test 123")

<script>
var e = new CustomEvent("testEvent"
        {
          detail: "test 123" }
        });
</script>

sendToWebEngine("EventFrontPlate", "testEvent", "'test 123'")

sendToWebEngine("EventFrontPlate", "testEvent", "{custom: 'test 123'}")

<script>
var e = new CustomEvent("testEvent"
        {
          detail: "{custom: 'test 123' }"
        });
</script>
