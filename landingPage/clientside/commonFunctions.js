var exceptionDict = {};
function getSubmitParameters(qId,exceptions,minRange){
    exceptionDict[qId] = (qId+","+minRange.toString()+","+exceptions).split(',');
}
function checkSubmitPoll(){
    for (var info of exceptionDict){
        var qId = info[0];
        var minChar = info[1];
        var exceptions = [];
        for (var i = 2; i < info.length;i++){
            exceptions.add(info[i]);
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