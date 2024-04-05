import psycopg2 as psy
from configure import config
import re

class PhonebookApp:
    """
    A simple phonebook application that allows users to manage contacts.
    """

    def __init__(self):
        """
        Initialize the PhonebookApp class.
        """
        self.connection = self.connect()
        self.create_tables()


    def connect(self):
        """
        Connect to the PostgreSQL database.
        """
        connection = None
        try:
            params = config()
            connection = psy.connect(**params)
            return connection
        except psy.Error as e:
            print(f"Error connecting to the database: {e}")
            raise


    def create_tables(self):
        """
        Create necessary tables in the database if they don't exist.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    email VARCHAR(30) NOT NULL
                )
            """)
            self.connection.commit()
            cursor.close()
        except psy.Error as e:
            print(f"Error creating table: {e}")
            raise


    def add_contact(self):
        """
        Add a new contact to the phonebook.
        """
        while True:
            name = input("Enter name: ").strip().title()
            if name == "":
                print("Name cannot be blank")
                continue
            phone = input("Enter phone number: ").strip()
            if not self.validate_phone(phone):
                print("Invalid phone number format. Please enter a valid phone number.")
                continue
            email = input("Enter email: ").strip()
            if not self.validate_email(email):
                print("Invalid email format. Please enter a valid email.")
                continue
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO contacts (name, phone, email) VALUES (%s, %s, %s)
                """, (name, phone, email))
                self.connection.commit()
                cursor.close()
                print("Contact added successfully.")
                break
            except psy.Error as e:
                print(f"Error adding contact: {e}")


    def validate_phone(self, phone):
        """
        Validate the format of a phone number.
        """
        return re.match(r'^[\d-]+$', phone)


    def validate_email(self, email):
        """
        Validate the format of an email address.
        """
        return re.match(r"^[\w\.-]+@[\w\.-]+$", email)


    def view_contact(self, contact_id):
        """
        View a contact's details.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
            if contact:
                print(contact)
            else:
                print("Contact not found.")
        except psy.Error as e:
            print(f"Error fetching contact: {e}")


    def view_contacts(self):
        """
        View all contacts.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM contacts")
            contacts = cursor.fetchall()
            cursor.close()
            if contacts:
                for contact in contacts:
                    print(contact)
            else:
                print("No contacts found.")
        except psy.Error as e:
            print(f"Error fetching contacts: {e}")
            raise


    def update_contact(self, contact_id):
        """
        Update a contact's details.
        """
        new_name = input("Enter new name: ").strip().title()
        new_phone = input("Enter new phone number: ").strip()
        new_email = input("Enter new email: ").strip()
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE contacts 
                SET name = %s, phone = %s, email = %s
                WHERE id = %s
            """, (new_name, new_phone, new_email, contact_id))
            self.connection.commit()
            cursor.close()
            print("Contact updated successfully.")
        except psy.Error as e:
            print(f"Error updating contact: {e}")


    def search_contact(self):
        """
        Search for contacts by name.
        """
        search_term = input("Enter name to search for: ").strip().title()
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, name FROM contacts WHERE name ILIKE %s
            """, ('%' + search_term + '%',))
            contacts = cursor.fetchall()
            cursor.close()
            if contacts:
                print("Matching contacts:")
                for contact in contacts:
                    print(f"{contact[0]}. {contact[1]}")
                    choice = input("Enter 1. to delete a contact OR 2. to view a contact detail OR 0. to exit: ")
                    if choice == "1":
                        self.choose_contact_for_deletion(contacts)
                    elif choice == "2":
                        self.choose_contact_to_view(contacts)
                    elif choice == "0":
                        break
                    else:
                        print("Invalid choice, choose a number from 0 to 2")
            else:
                print("No matching contacts found.")
        except psy.Error as e:
            print(f"Error searching contacts: {e}")


    def delete_contact(self, contact_id):
        """
        Delete a contact from the phonebook.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
            self.connection.commit()
            cursor.close()
            print("Contact deleted successfully.")
        except psy.Error as e:
            print(f"Error deleting contact: {e}")


    def choose_contact_to_view(self, contacts):
        """
        Select a contact to view its details.
        """
        contact_ids = [contact[0] for contact in contacts]
        choice = input("Enter ID of contact to view (0 to cancel): ").strip()
        if choice.isdigit():
            choice_id = int(choice)
            if choice_id in contact_ids:
                self.view_contact(choice_id)
            elif choice_id == 0:
                print("Viewing canceled.")
            else:
                print("Invalid contact ID. Please enter a valid ID.")
        else:
            print("Invalid input. Please enter a valid contact ID.")


    def choose_contact_for_deletion(self, contacts):
        """
        Select a contact to delete it.
        """
        contact_ids = [contact[0] for contact in contacts]
        choice = input("Enter ID of contact to delete (0 to cancel): ").strip()
        if choice.isdigit():
            choice_id = int(choice)
            if choice_id in contact_ids:
                self.delete_contact(choice_id)
            elif choice_id == 0:
                print("Deletion canceled.")
            else:
                print("Invalid contact ID. Please enter a valid ID.")
        else:
            print("Invalid input. Please enter a valid contact ID.")


    def delete_selected_contact(self):
        """
        Delete a contact based on the entered name.
        """
        search_term = input("Enter name you want to delete from contact: ").strip().title()
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, name FROM contacts WHERE name ILIKE %s
            """, ('%' + search_term + '%',))
            contacts = cursor.fetchall()
            cursor.close()
            if contacts:
                print("Matching contacts:")
                for contact in contacts:
                    print(f"{contact[0]}. {contact[1]}")
                    self.choose_contact_for_deletion(contacts)
            else:
                print("No matching contacts found.")
        except psy.Error as e:
            print(f"Error searching contacts: {e}")


    def view_selected_contact(self):
        """
        View details of a contact based on the entered name.
        """
        search_term = input("Enter name you want to view details of: ").strip().title()
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, name FROM contacts WHERE name ILIKE %s
            """, ('%' + search_term + '%',))
            contacts = cursor.fetchall()
            cursor.close()
            if contacts:
                print("Matching contacts:")
                for contact in contacts:
                    print(f"{contact[0]}. {contact[1]}")
                    self.choose_contact_to_view(contacts)
            else:
                print("No matching contacts found.")
        except psy.Error as e:
            print(f"Error searching contacts: {e}")


    def close_connection(self):
        """
        Close the database connection.
        """
        if self.connection is not None:
            self.connection.close()
            print("Connection closed.")


    def main_menu(self):
        """
        Display the main menu of the phonebook application.
        """
        print("Welcome to ROLA Phonebook Storage Center")
        while True:
            print("\nPHONEBOOK MENU:")
            print("1. Add Contact")
            print("2. View All Contacts")
            print("3. Search Contacts")
            print("4. View A Contact")
            print("5. Update Contact")
            print("6. Delete Contact")
            print("7. Quit")
            choice = input("Enter your choice (1-7): ").strip()
            if choice == "1":
                self.add_contact()
            elif choice == "2":
                self.view_contacts()
            elif choice == "3":
                self.search_contact()
            elif choice == "4":
                self.view_selected_contact()
            elif choice == "5":
                contact_id = input("Enter ID of contact to update: ").strip()
                self.update_contact(contact_id)
            elif choice == "6":
                self.delete_selected_contact()
            elif choice == "7":
                clarity = input("Are you sure you want to exit? 1) Yes (OR BLANK TO EXIT) OR 2) No: ").strip()
                if clarity == "1" or clarity == "":
                    self.close_connection()
                    print("Exiting the phonebook app...")
                    break
                else:
                    continue
            else:
                print("Invalid choice. Please enter a valid option.")



if __name__ == "__main__":
    phonebook = PhonebookApp()
    phonebook.main_menu()
