async function register() {

    const username =
        document.getElementById(
            "username"
        ).value;

    const email =
        document.getElementById(
            "email"
        ).value;

    const tenant =
        document.getElementById(
            "tenant"
        ).value;

    const password =
        document.getElementById(
            "password"
        ).value;

    const confirmPassword =
        document.getElementById(
            "confirmPassword"
        ).value;

    const error =
        document.getElementById(
            "error"
        );

    error.innerText = "";

    if (
        password !==
        confirmPassword
    ) {

        error.innerText =
            "Passwords do not match";

        return;
    }

    try {

        const response =
            await fetch(
                "/api/register/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        username:
                            username,
                        email:
                            email,
                        password:
                            password,
                        tenant_name:
                            tenant
                    })
                }
            );

        const data =
            await response.json();

        if (
            response.status === 201
        ) {

            alert(
                "Registration successful. Please login."
            );

            window.location.href =
                "/";

            return;
        }

        error.innerText =
            JSON.stringify(data);

    } catch (err) {

        error.innerText =
            "Registration failed.";
    }
}