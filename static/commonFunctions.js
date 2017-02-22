var exceptionDict = [];
function getSubmitParameters(qId,exceptions,minRange){
    exceptionDict.push((qId+","+minRange.toString()+","+exceptions).split(','));
}
function checkSubmitPoll(){
    for (var n = 0; n < exceptionDict.length;n++){
        var qId = exceptionDict[n][0];
        var minChar = exceptionDict[n][1];
        var exceptions = [];
        for (var i = 2; i < exceptionDict[n].length;i++){
            exceptions.push(exceptionDict[n][i]);
        }
        var answer = document.getElementById("q:"+qId).value;
        var validAnswer = answer.length > minChar;
        if(validAnswer){
            for(var i = 0; i < exceptions.length; i++){
                validAnswer = !answer.includes(exceptions[i]);
                if(!validAnswer){
                    window.alert("Question number "+qId.toString()+"'s input is invalid");
                    return;
                }
            }
        } else {
            window.alert("Question number "+qId.toString()+"'s answer must be at least "+minChar.toString()+" characters long");
            return;
        }
    }
    if(validAnswer)document.getElementById("pollForm").submit();
}
function show(id){
    doc =document.getElementById(id);
    doc.style.visibility = "visible";
    doc.style.height = "";
    doc.style.width = "";
    doc.style.display = "";
}
function collapse(id){
    doc = document.getElementById(id);
    doc.style.visibility = "collapse";
    doc.style.height = "0px";
    doc.style.width = "0px";
    doc.style.display = "none";
}
function iframeInsert(id,content){
        var iframe = document.getElementById(id).contentWindow.document;
        iframe.open();
        iframe.write("<link rel=\"stylesheet\" href=\"/static/stylesheets/main.css\">"+content);
        iframe.close();
    }