console.log("login.js loaded");
let loginForm = document.getElementById("login_form");
let errorMessage = null;
function oldErrorCheck(){
    var oldErrorMessage = document.getElementById("errorMessage");
    if (oldErrorMessage === null){ //Finish this!
        return false;
    }
    else{
        return true;
    }
}

function submitLogin(event){
    event.preventDefault();
    if (!loginForm[0].value.includes("@")){
        errorMessage = document.createElement("p");
        errorMessage.id = "errorMessage";
        errorMessage.style.color = "red";
        errorMessage.innerHTML = "Please enter a valid email address";
        mainBody.appendChild(errorMessage);
        return;
    }
    var loginData = {
        "username": loginForm[0].value,
        "password": loginForm[1].value
    };
    $.ajax({
        type: "POST",
        url: "/users/login/validate",
        data: JSON.stringify(loginData),
        success: function(response){
            if (response === "success"){
                window.location.replace("/");
            }
            else if (response === "usernotexist"){
                var mainBody = document.getElementById("page_mainbody_home");
                if (oldErrorCheck() === false){
                    errorMessage = document.createElement("p");
                    errorMessage.id = "errorMessage";
                    errorMessage.style.color = "red";
                    errorMessage.innerHTML = "Username or Password is incorrect";
                    mainBody.appendChild(errorMessage);
                }
            }
            else{
                var mainBody = document.getElementById("page_mainbody_home");
                if (oldErrorCheck() === false){
                    errorMessage = document.createElement("p");
                    errorMessage.id = "errorMessage";
                    errorMessage.style.color = "red";
                    errorMessage.innerHTML = "An server error occured";
                    mainBody.appendChild(errorMessage);
                }
            }
        }
    });
}

loginForm.addEventListener("submit", submitLogin);