const sidebarLinks = document.querySelectorAll(".sidebar-links");
const displaySections = document.querySelectorAll(".display-container");
var usersView = document.querySelector("#users .split-view .left-box");

sidebarLinks.forEach((link) => {
    link.addEventListener("click", () => {
        sidebarLinks.forEach((item) => {
            item.classList.remove("active");
        })
        link.classList.add("active");

        const target = link.getAttribute("data-target");
        if (target == "users") {
            fetchUsers()
        }
        displaySections.forEach((section) => {
            section.style.display = "none";
            if (section.id === target) {
                section.style.display = "block";
            }
        });
    });
});

function fetchUsers()
{
fetch("/admin/users")
            .then((response) => response.json())
            .then((users) => {
                // Clear previous content
                usersView.innerHTML = '<h2>OETMS USERS LIST</h2>';

                // Iterate over users and create HTML elements
                users.forEach((user) => {
                    const userElement = document.createElement("div");
                    userElement.classList.add("user-box")
                    userElement.innerHTML = `
                        <div class="user-heading">
                            <p><span>Fullname</span>: ${user.fullname}</p>
                            <p><span>Email</span>: ${user.email}</p>
                        </div>
                        
                        <p><span>Role</span>: ${user.role}</p>
                        ${user.role === 'worker' ? `<p><span>Employed</span>: ${user['Employment Status'] == 1 ? "Yes" : "No"}</p>` : ''}
                        <div class="user-btns">
                        <button class="btn" onclick="getUserDetails(${user.id}, '${user.role}')">View</button>
                        <button class="btn">Delete</button>
                        </div>
                        `;
                    usersView.appendChild(userElement);
                });
            });
}

fetchUsers()



function getUserDetails(userId, userRole) {
    // Fetch user details based on the userId and userRole
    fetch(`/admin/user/${userId}?role=${userRole}`)
        .then((response) => response.json())
        .then((user) => {
            // Display user details in the right box
            const userDetailsBox = document.querySelector(".individual-user-details");
            userDetailsBox.innerHTML = `
                <div class="heading">
                <h2>OETMS</h2>
                <h2>WORKER PROFILE</h2>
                </div>
                <div class="body">
                    <div class="row">
                        <h3>Fullname:</h3> <p>${user.fullname}</p>
                    </div>
                    <div class="row">
                        <h3>Email:</h3> <p>${user.email}</p>
                    </div>
                    <div class="row">
                        <h3>Role:</h3> <p>${user.role}</p>   
                    </div>
                    <div class="row">
                        ${user.role === 'worker' ? `<h3>Employed</h3>: ${user['EMPLOYED'] == 1 ? "Employed" : "Not Employed"}</p>` : ''}
                    </div>
                    <div class="row">
                        <h3>Work Type:</h3> <p>${user.work_type}</p>
                    </div>
                    <div class="row">
                        <h3>Work Location:</h3> <p>${user.work_location}</p>
                    </div>
                    <div class="row">
                        <h3>Employer Name:</h3> <p>${user.employer_name}</p>
                    </div>
                    <div class="row">
                        <h3>Employer Contact:</h3> <p>${user.employer_contact}</p>
                    </div>
                    <div class="row">
                        <h3>Employemnt Start Date:</h3> <p>${user.employment_start_date}</p>
                    <div>
                </div>
                <button class="btn">Print</button>
            `;
        });
}
