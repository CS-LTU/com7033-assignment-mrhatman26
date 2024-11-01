console.log("submission.js loaded");
let submissionForm = document.getElementById("submission_form");
let mainBody = document.getElementById("page_mainbody_home");
let errorMessage = null;

function oldErrorCheck(){
    var oldErrorMessage = document.getElementById("errorMessage");
    if (oldErrorMessage === null){
        return false;
    }
    else{
        return true;
    }
}

function submitData(event){
    event.preventDefault();
    var submissionData = {
        "patient_gender": submissionForm[0].value,
        "patient_age": submissionForm[1].value,
        "patient_hyperT": submissionForm[2].value,
        "patient_hDisease": submissionForm[3].value,
        "patient_married": submissionForm[4].value,
        "patient_work_type": submissionForm[5].value,
        "patient_residence_type": submissionForm[6].value,
        "patient_avg_gLevel": submissionForm[7].value,
        "patient_bmi": submissionForm[8].value,
        "patient_smoked": submissionForm[9].value,
        "patient_stroke": submissionForm[10].value
    };
    $.ajax({
        type: "POST",
        url: "/submission/validate/",
        data: JSON.stringify(submissionData),
        success: function(response){
            if (response === "success"){
                window.location.replace("/submission/validate/");
            }
            else if (response === "unkown"){
                if (oldErrorCheck() === false){
                    var mainBody = document.getElementById("page_mainbody_home");
                    errorMessage = document.createElement("p");
                    errorMessage.id = "errorMessage";
                    errorMessage.style.color = "red";
                    errorMessage.innerHTML = "An unkown error ocurred";
                    mainBody.appendChild(errorMessage);
                }
                else{
                    errorMessage.innerHTML = "An unkown error ocurred";
                }
            }
            else{
                if (oldErrorCheck() === false){
                    var mainBody = document.getElementById("page_mainbody_home");
                    errorMessage = document.createElement("p");
                    errorMessage.id = "errorMessage";
                    errorMessage.style.color = "red";
                    errorMessage.innerHTML = "A server error occured";
                    mainBody.appendChild(errorMessage);
                }
                else{
                    errorMessage.innerHTML = "A server error occured";
                }
            }
        }
    });
}

submissionForm.addEventListener("submit", submitData);