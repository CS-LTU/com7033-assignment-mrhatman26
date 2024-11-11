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
    //Make sure password does not contain text from the other boxes
    if (signupForm[2].value.includes(signupForm[0].value.split(" ")[0]) || signupForm[2].value.includes(signupForm[0].value.split(" ")[1]) || signupForm[2].value.includes(signupForm[1].value.split("@")[0])){
        if (oldErrorCheck() === false){
            var mainBody = document.getElementById("page_mainbody_home");
            errorMessage = document.createElement("p");
            errorMessage.id = "errorMessage";
            errorMessage.style.color = "red";
            errorMessage.innerHTML = "Password cannot contain your email or name.";
            mainBody.appendChild(errorMessage);
        }
        else{
            errorMessage.innerHTML = "Password cannot contain your email or name.";
        }
        return;
    }
    //Make sure password and confirm password match
    if (signupForm[3].value !== signupForm[2].value){
        if (oldErrorCheck() === false){
            var mainBody = document.getElementById("page_mainbody_home");
            errorMessage = document.createElement("p");
            errorMessage.id = "errorMessage";
            errorMessage.style.color = "red";
            errorMessage.innerHTML = "Reconfirm password does not match password";
            mainBody.appendChild(errorMessage);
        }
        else{
            errorMessage.innerHTML = "Reconfirm password does not match password";
        }
        return;
    }
    //Phone number correction
    if (!signupForm[4].value.includes(" ")){
        signupForm[4].value = signupForm[4].value.slice(0, 5) + " " + signupForm[4].value.slice(5);
    }
    var signupData = {
        "fullname": signupForm[0].value,
        "email": signupForm[1].value,
        "password": signupForm[2].value,
        "phone": signupForm[4].value
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