console.log("signup.js loaded");
let signupForm = document.getElementById("signup_form");
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

function submitLogin(event){
    event.preventDefault();
    //Email check
    if (!signupForm[1].value.includes("@")){
        errorMessage = document.createElement("p");
        errorMessage.id = "errorMessage";
        errorMessage.style.color = "red";
        errorMessage.innerHTML = "Please enter a valid email address";
        mainBody.appendChild(errorMessage);
        return;
    }
    //Password check
    
    var signupData = {
        "fullname": signupForm[0].value,
        "email": signupForm[1].value,
        "password": signupForm[2].value,
        "phone": signupForm[3].value
    };
    $.ajax({
        type: "POST",
        url: "/users/signup/validate",
        data: JSON.stringify(signupData),
        success: function(response){
            if (response === "success"){
                window.location.replace("/users/login");
            }
            else if (response === "userexists"){
                if (oldErrorCheck() === false){
                    var mainBody = document.getElementById("page_mainbody_home");
                    errorMessage = document.createElement("p");
                    errorMessage.id = "errorMessage";
                    errorMessage.style.color = "red";
                    errorMessage.innerHTML = "Username already in use";
                    mainBody.appendChild(errorMessage);
                }
                else{
                    errorMessage.innerHTML = "Username already in use";
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

signupForm.addEventListener("submit", submitLogin);