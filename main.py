from sql_server import setup_database
connector, cursor = setup_database()


class User:
    userlist = []

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        User.userlist.append(self)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        try:
            if not all(x.isalpha() or x.isspace() for x in value):
                raise ValueError
        except ValueError:
            print("Name should only contain letters or spaces")
            while not all(x.isalpha() or x.isspace() for x in value):
                value = input("Re-enter your name:")
        self.__name = value

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        try:
            if "@" not in value or ".com" not in value:
                raise SyntaxError
        except SyntaxError:
            print("Enter proper email")
            value = input("Re-enter your email:")
        self.__email = value

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, value):
        self.__password = value

    @staticmethod
    def record_info():
        name = input("Enter your name: ")
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        return name, email, password

    @staticmethod
    def login(choice):
        uemail = input("Enter email: ")
        pword = input("Enter password: ")
        for i in User.userlist:
            if uemail != i.email:
                continue
            if pword != i.password:
                print("Password is incorrect")
                return None
            if isinstance(i, Seeker) and choice != "1":
                print("Wrong user type")
                return
            if isinstance(i, Employer) and choice != "2":
                print("Wrong user type")
                return
            return i
        print("Email not found")
        return None


class Seeker(User):
    def __init__(self, seek_id, name, email, description, skills, password, status):
        super().__init__(name, email, password)
        if type(seek_id) == tuple:
            self.seek_id = seek_id[0]
        else:
            self.seek_id = seek_id
        self.description = description
        self.skills = skills.strip().lower().split(",")
        if status is None:
            self.status = []
        else:
            self.status = status
        seeker_list.append(self)

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    @property
    def skills(self):
        return self.__skills

    @skills.setter
    def skills(self, value):
        self.__skills = value

    @staticmethod
    def record_info():
        name, email, password = User.record_info()
        while not all(x.isalpha() or x.isspace() for x in name):
            name = input("Re-enter your name:")
        while "@" not in email or ".com" not in email:
            email = input("Re-enter your email:")
        skills = input("Enter your skills (Separate each skill by a comma): ")
        description = input("Enter a description for your profile: ")
        data = """INSERT INTO job_seekers(name, email, description, skills, password) VALUES(%s, %s, %s, %s, %s)
            """
        values = name, email, description, skills, password
        cursor.execute(data, values)
        connector.commit()
        cursor.execute("SELECT id FROM job_seekers ORDER BY id DESC;")
        seeker_id = cursor.fetchone()
        return Seeker(seeker_id, name, email, description, skills, password, [])

    def recommended(self):
        recs = []
        for i in joblist:
            count = 0  # Reset count for each job
            for j in i.required_skills:
                if str(j) in self.skills:
                    count += 1
            if (count / len(i.required_skills)) > 0.6:
                recs.append(i)
        return recs

    def display_recs(self):
        recs = self.recommended()
        print("-"*40)
        if len(recs) == 0:
            print("No jobs available at the moment.")
        for i in recs:
            print(f"{' ' * 20}Title: {i.title}")
            print("Description: ", i.description)
            print("Required Skills: ", ','.join(i.required_skills))
            print(f"Posted by {i.employer.name}")
            print(f"Job ID: {i.job_id}")

        print("Select option:")
        print("1. Apply to job")
        print("2. Go back")
        print("3. Exit")
        x = input()
        if x == '2':
            return
        elif x == '3':
            exit()
        elif x == '1':
            y = input("Enter ID of job you would like to apply to: ")
            self.apply(y)
        else:
            print("Invalid Choice")
            self.display_recs()

    def apply(self, job_id):
        for job in joblist:
            if str(job.job_id) == job_id:
                obj_and_jobid = str([self.seek_id, job_id])
                if len(job.employer.applicants) != 0:
                    job.employer.applicants.append((self, job_id))
                    cursor.execute(f"""UPDATE employers SET applicants_id=CONCAT_WS(';',applicants_id,"{obj_and_jobid}") WHERE id={job.employer.employer_id}""")
                else:
                    job.employer.applicants.append((self, job_id))
                    cursor.execute(f"""UPDATE employers SET applicants_id="{obj_and_jobid}" WHERE id={job.employer.employer_id}""")
                connector.commit()
                print(f"Successfully applied for the job: {job.title}")
                return
        print("Invalid job ID. Application failed.")

    def view_status(self):
        if len(self.status) == 0:
            print("No new updates")
        else:
            for i in self.status:
                item = eval(str(i))
                for j in joblist:
                    if str(j.job_id) == str(item[0]):
                        job = j
                if item[1] is True:
                    print(f"Congratulations your application for {job.title} posted by {job.employer.name} has been accepted.")
                    print(f"Get in touch with the employer with this: {item[2]}")
                else:
                    print(f"Your job application for {job.title} posted by {job.employer.name} has unfortunately been rejected.")

class Employer(User):
    def __init__(self, employer_id, name, email, password, applicants):
        super().__init__(name, email, password)
        if type(employer_id) == tuple:
            self.employer_id = employer_id[0]
        else:
            self.employer_id = employer_id
        self.applicants = applicants
        employer_list.append(self)

    @staticmethod
    def record_info():
        name, email, password = User.record_info()
        while not all(x.isalpha() or x.isspace() for x in name):
            name = input("Re-enter your name:")
        while "@" not in email or ".com" not in email:
            email = input("Re-enter your email:")
        data = """INSERT INTO employers(name, email, password) VALUES(%s, %s, %s)
                    """
        values = name, email, password
        cursor.execute(data, values)
        connector.commit()
        cursor.execute("SELECT id FROM employers ORDER BY id DESC;")
        emp_id = cursor.fetchone()
        return Employer(emp_id[0], name, email, password, [])

    def post_job(self):
        name = input("Enter name of the job: ")
        skills = input("Enter required skills (separated by comma): ")
        description = input("Enter job description: ")
        data = """INSERT INTO jobs(title, skills, description, employer_id) VALUES(%s, %s, %s, %s)
                    """
        values = name, skills, description, self.employer_id
        cursor.execute(data, values)
        connector.commit()
        cursor.execute("SELECT id FROM jobs ORDER BY id DESC;")
        job_id = cursor.fetchone()
        job_obj = Job(job_id, name, skills, description, self)
        joblist.append(job_obj)
        print(f"Job '{name}' successfully posted.")

    def see_applicants(self):
        """Function to display applicants of employer"""
        count = 0
        for i in self.applicants:
            for job in joblist:
                if str(job.job_id) == i[1]:
                    applied_to = job
            print(f"Job Title: {applied_to.title}, Job ID: {applied_to.job_id}")
            print("Applicants:")
            print(f" - Name:{i[0].name}, Skills:{i[0].skills}, ")
            print(f"   Description:{i[0].description}, id:{i[0].seek_id}")
            print()
            count += 1
        if count == 0:
            print("No applicants to show")
            return

        print("Select option:")
        print("1. Approve application")
        print("2. Reject application")
        print("3. Go back")
        print("4. Exit")
        x = input()
        if x == '1':
            y = input("Enter the id of the applicant you wish to approve: ")
            z = input("Enter the job id of the job you wish to approve them for: ")
            a = input("Enter your contact information to allow applicant to contact you: ")
            obj_and_jobid = str([z, True, a])
            for j in joblist:
                if str(j.job_id) == z:
                    approved_job = j
            if "approved_job" not in locals():
                print("Job not found. Check the entered ID and try again.")
                return
            for i in seeker_list:
                if str(i.seek_id) == y:
                    i.status.append([approved_job.job_id, True, a])
                    cursor.execute(f"""UPDATE job_seekers SET status=CONCAT_WS(';',status,"{obj_and_jobid}") WHERE id={i.seek_id}""")
                    connector.commit()
                    print("Applicant has been informed of your decision successfully.")
                    return
            print("Applicant ID not found. Check the entered ID and try again.")
        if x == '2':
            y = input("Enter the id of the applicant you wish to reject: ")
            z = input("Enter the job id of the job you wish to reject them from: ")
            obj_and_jobid = str([z, False, None])
            for j in joblist:
                if str(j.job_id) == z:
                    reject = j
            if "reject" not in locals():
                print("Job not found. Check the entered ID and try again.")
                return
            for i in seeker_list:
                if str(i.seek_id) == y:
                    i.status.append([reject.job_id, False, None])
                    cursor.execute(f"""UPDATE job_seekers SET status=CONCAT_WS(';',status,"{obj_and_jobid}") WHERE id={i.seek_id}""")
                    connector.commit()
                    print("Applicant has been informed of your decision successfully.")
                    return
            print("Applicant ID not found. Check the entered ID and try again.")
        elif x == '3':
            return
        elif x == '4':
            exit()


class Job:

    def __init__(self, id, title, skills, description, employer):
        if type(id) == tuple:
            self.job_id = id[0]
        else:
            self.job_id = id
        self.employer = employer
        self.title = title
        self.required_skills = skills.strip().lower().split(",")
        self.description = description


joblist = []
seeker_list = []
employer_list = []
userlist = []
applicant_list = []


def get_from_db():
    cursor.execute("SELECT * FROM job_seekers;")
    seek = cursor.fetchall()
    for i in seek:
        try:
            status = i[-1].split(";")
        except:
            status = None
        obj = Seeker(*i[:-1], status)
        userlist.append(obj)
    cursor.execute("SELECT * FROM employers;")
    emps = cursor.fetchall()
    for i in emps:
        if i[-1] == None:
            pass
        else:
            for applicant in i[-1].split(';'):
                applicant = eval(applicant)
                for seeker in seeker_list:
                    if seeker.seek_id == applicant[0]:
                        applicant_list.append((seeker, applicant[1]))
        obj = Employer(*i[:-1], applicant_list)
        userlist.append(obj)
    cursor.execute("SELECT * FROM jobs;")
    jobs = cursor.fetchall()
    for i in jobs:
        for emp in employer_list:
            if i[-1] == emp.employer_id:
                emp_obj = emp
        obj = Job(*i[:-1], emp_obj)

        joblist.append(obj)

if __name__ == "__main__":
    get_from_db()
    while True:
        print("Welcome to JobJet")
        print("-" * 40)
        print("Select user type:")
        print("1. Job Seeker")
        print("2. Employer")
        print("3. Exit")
        choice = input()

        if choice == "1":
            obj = None
            choice2 = None
            while obj is None:
                print("Select option:")
                print("1. Log into account")
                print("2. Create a new account")
                print("3. Go back")
                choice2 = input()
                if choice2 == "1":
                    obj = User.login(choice)
                elif choice2 == "2":
                    obj = Seeker.record_info()
                elif choice2 == "3":
                    break
                else:
                    print("Invalid choice")
                    continue

            if obj is not None:
                while True:
                    print("Select option:")
                    print("1. View recommended jobs")
                    print("2. View applications status")
                    print("3. Go back")
                    choice3 = input()
                    if choice3 == "1":
                        obj.display_recs()
                    elif choice3 == "3":
                        break
                    elif choice3 == "2":
                        obj.view_status()
                    else:
                        print("Invalid choice")

        elif choice == "2":
            obj = None
            choice2 = None
            while obj is None:
                print("Select option:")
                print("1. Log into account")
                print("2. Create a new account")
                print("3. Go back")
                choice2 = input()
                if choice2 == "1":
                    obj = User.login(choice)
                elif choice2 == "2":
                    obj = Employer.record_info()
                elif choice2 == "3":
                    break
                else:
                    print("Invalid choice")
                    continue

            if obj is not None:
                while True:
                    print("Select option:")
                    print("1. Post a job")
                    print("2. See applicants")
                    print("3. Go back")
                    choice3 = input()
                    if choice3 == "1":
                        obj.post_job()
                    elif choice3 == "2":
                        obj.see_applicants()
                    elif choice3 == "3":
                        break
                    else:
                        print("Invalid choice")

        elif choice == "3":
            break
        else:
            print("Invalid choice")
