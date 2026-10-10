from db import get_connection


class UserRepository:

    def get_by_email(self, email):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT user_id, email, password_hash, role
                FROM dbo.users
                WHERE email = ?
                """,
                email
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "user_id": row[0],
                "email": row[1],
                "password_hash": row[2],
                "role": row[3],
            }

        finally:
            cursor.close()
            connection.close()

    def create_user(self, email, password_hash, role="user"):
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO dbo.users (email, password_hash, role)
                OUTPUT INSERTED.user_id
                VALUES (?, ?, ?)
                """,
                email,
                password_hash,
                role
            )

            user_id = cursor.fetchone()[0]
            connection.commit()
            return user_id

        finally:
            cursor.close()
            connection.close()
