const sidebarLinks = document.querySelectorAll(".sidebar-links");
const displaySections = document.querySelectorAll(".display-container");
var usersView = document.querySelector("#users .split-view .left-box");
var documentsView = document.querySelector("#documents .split-view .left-box");
var incidentView = document.querySelector("#incidents .incident-view");


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
        if (target == "documents")
        {
            fetchDocuments()
        }
        if (target == "incidents")
        {
            fetchIncidents()
        }

        displaySections.forEach((section) => {
            section.style.display = "none";
            if (section.id === target) {
                section.style.display = "block";
            }
        });
    });
});

//  Function to get all users in the db, both workers and employers
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
                        <p><span>Location</span>: ${user.location}</p>
                        ${user.role === 'worker' ? `<p><span>Employed</span>: ${user['Employment Status'] == 1 ? "Yes" : "No"}</p>` : ''}
                        <div class="user-btns">
                        <button class="btn" onclick="getUserDetails(${user.id}, '${user.role}', '${user.location}')">View</button>
                        <button class="btn">Delete</button>
                        </div>
                        `;
                    usersView.appendChild(userElement);
                });
            });
}

fetchUsers()


//  Function to get profile information of an individual user
function getUserDetails(userId, userRole, userLocation) {
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
                    </div>
                    <div class="row">
                        <h3>Current User Location:</h3> <p>${userLocation}</p>
                    </div>
                </div>
                <button class="btn" onclick="convertToPdf('.individual-user-details', '${user.first}-profile.pdf')">Print</button>
            `;
        });
}


function convertToPdf(elementClass, filename) {
    const element = document.querySelector(elementClass);
    html2pdf(element, {
        margin: 1,
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { dpi: 192, letterRendering: true },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    });
}


function fetchDocuments() {
fetch("/admin/documents")
.then(response => response.json())
.then((users) => {
    //  Clear Previous Content
    documentsView.innerHTML = `<h2>OETMS USER DOCUMENTS</h2>`

    //  Iterate over users and create html elements
    users.forEach((user) => {
        const userElement = document.createElement("div");
        userElement.classList.add("user-box")
        userElement.innerHTML = `
            <div class="user-heading">
                <p><span>Fullname</span>: ${user.fullname}</p>
                <p><span>Email</span>: ${user.email}</p>
            </div>
            <p><span>User Role: </span> ${user.role}</p>
            <p><span>Document Type: </span> ${user.document_type}</p>
            <p><span>Document Name: </span> ${user.document_name}</p>
            <div class="user-btns">
            <button class="btn" onclick="getUserDocuments('${user.document_location}', '${user.doc_id}', '${user.role}')">View Document</button>
            </div>
            `;
        documentsView.appendChild(userElement);
    })
})
}

//  Function to showcase an individual user's document
function getUserDocuments(documentPath, documentId, role)
{

    // Remove the leading dot (.) from the documentPath
    documentPath = documentPath.replace(/^\./, '');
     
    const documentView = document.querySelector(".individual-document-view");
    documentView.innerHTML = `
        <div class="heading">
            <h2>OETMS</h2>
            <h2>USER DOCUMENT</h2>
        </div>
        <div class="body">
            <embed src="${documentPath}" type="application/pdf" width="100%" height="500px">
        </div>
        <div class="btns">
        <button class="btn" onclick="verifyDocument('${documentId}', '${role}')">Approve</button>
            <button class="btn">Reject</button>
        </div>
    `;
}

function verifyDocument(documentId, role) {
    fetch("/admin/verify_document", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `document_id=${documentId}&role=${role}`,
    })
        .then((response) => response.json())
        .then((data) => {
            console.log(data.message);
            alert("Document Verified Successfully")
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("An error occured while verifying the document")
        });
}


function fetchIncidents() {
    fetch("/admin/incidents")
        .then((response) => response.json())
        .then((incidents) => {
            incidentView.innerHTML = "<h2>OETMS WORKER INCIDENTS</h2>";

            incidents.forEach((incident) => {
                const incidentElement = document.createElement("div");
                incidentElement.classList.add("user-box")
                incidentElement.innerHTML = `
                    <div class="incident-heading">
                        <p><span>Date</span>: ${incident.date}</p>
                        <p><span>Location</span>: ${incident.location}</p>
                    </div>
                    <p><span>Reported By</span>: ${incident.first_name} ${incident.last_name}</p>
                    <p><span>Description</span>: ${incident.description}</p>
                    <div>
                        <label for="inc-status" style="color: goldenrod;">Status: </label>
                        <select id="inc-status">
                            <option value="inprogress" ${incident.status === 'inprogress' ? 'selected' : ''}>In Progress</option>
                            <option value="pending" ${incident.status === 'pending' ? 'selected' : ''}>Pending</option>
                            <option value="resolved" ${incident.status === 'resolved' ? 'selected' : ''}>Resolved</option>
                        </select>
                    </div>
                    <div class="comment-box">
                        <textarea class="admin-comment" placeholder="Add admin comment..."></textarea>
                        <button class="btn" onclick="addComment(${incident.id})">Add Comment</button>
                    </div>
                    `;
                incidentView.appendChild(incidentElement);
            });
        });
}


function addComment(incidentId) {
    const commentElement = document.querySelector('.admin-comment');
    const comment = commentElement.value;
    const status = document.getElementById('inc-status').value;
    fetch(`/admin/incidents/${incidentId}/comment`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ comment, status })
    })
        .then((response) => response.json())
        .then((data) => {
            console.log(data); // Handle success message
            alert("Comment Added Successfully")
        })
        .catch((error) => {
            console.error("Error:", error);
            // Handle error
            alert("An error occured while adding the comment")
        });
}