console.log("modifysub.js loaded");
let modifysubForm = document.getElementById("modifysub_form");
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
    var modifysubData = {
        "patient_gender": modifysubForm[0].value,
        "patient_age": modifysubForm[1].value,
        "patient_hyperT": modifysubForm[2].value,
        "patient_hDisease": modifysubForm[3].value,
        "patient_married": modifysubForm[4].value,
        "patient_work_type": modifysubForm[5].value,
        "patient_residence_type": modifysubForm[6].value,
        "patient_avg_gLevel": modifysubForm[7].value,
        "patient_bmi": modifysubForm[8].value,
        "patient_smoked": modifysubForm[9].value,
        "patient_stroke": modifysubForm[10].value
    };
    $.ajax({
        type: "POST",
        url: "/users/account/submission/modify/validate/",
        data: JSON.stringify(modifysubData),
        success: function(response){
            if (response === "success"){
                window.location.replace("/users/account/");
            }
            else if (response === "nolink"){
                if (oldErrorCheck() === false){
                    var mainBody = document.getElementById("page_mainbody_home");
                    errorMessage = document.createElement("p");
                    errorMessage.id = "errorMessage";
                    errorMessage.style.color = "red";
                    errorMessage.innerHTML = "You have no submitted data to modify";
                    mainBody.appendChild(errorMessage);
                }
                else{
                    errorMessage.innerHTML = "You have no submitted data to modify";
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

modifysubForm.addEventListener("submit", submitData);