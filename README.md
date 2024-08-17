# AcademicConnect

AcademicConnect is a backend project designed to facilitate interactions within an academic community. The platform enables professors and students to connect, manage profiles, and engage in meaningful discussions. It also provides administrative tools for managing the academic environment, including professor membership and permissions.

## Features

- **User Authentication:**
  - Login and Register functionality for users.
  - Profile management for both students and professors.

- **Professor Management:**
  - View a paginated list of professors.
  - Professors can view and manage their profile, including academic achievements like the number of publications.
  - Professors can ban or unban students from commenting on their profiles.

- **Student Management:**
  - View a paginated list of students.
  - View the list of students under a specific professor.
  
- **Commenting System:**
  - Professors and students can comment on professor profiles.
  - Banned students are restricted from commenting, with bans managed through the professor's panel.

- **Banning System:**
  - Professors have the ability to ban or unban students from commenting on their profiles.

- **Following System:**
  - Users can follow each other to stay updated on their activities.

- **Admin Panel:**
  - Admins can manage professor membership in the academic association.
  - Admins have the authority to add or remove professors from the system.
 ## Installation

1. **Install dependencies:**

   Install the required dependencies using:

   ```bash
   pip install -r requirements.txt
2. **configure  your .env:**

   Create a .env file in the root directory of the project to store your secret key and other environment variables.
