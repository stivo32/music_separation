from contextlib import asynccontextmanager
from typing import Callable, Optional, AsyncGenerator
from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import text
from functools import wraps

from fourier.dao.database import async_session_maker


class DatabaseSessionManager:
    """
    Class for managing asynchronous database sessions, including support for transactions and FastAPI dependencies.
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker

    @asynccontextmanager
    async def create_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Creates and provides a new database session.
        Ensures the session is closed after usage.
        """
        async with self.session_maker() as session:
            try:
                yield session
            except Exception as e:
                logger.error(f"Error while creating a database session: {e}")
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def transaction(self, session: AsyncSession) -> AsyncGenerator[None, None]:
        """
        Manages a transaction: commit on success, rollback on error.
        """
        try:
            yield
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.exception(f"Transaction error: {e}")
            raise

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        FastAPI dependency that returns a session without transaction management.
        """
        async with self.create_session() as session:
            yield session

    async def get_transaction_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        FastAPI dependency that returns a session with transaction management.
        """
        async with self.create_session() as session:
            async with self.transaction(session):
                yield session

    def connection(self, isolation_level: Optional[str] = None, commit: bool = True):
        """
        Decorator for managing a session with optional configuration for isolation level and commit.

        Parameters:
        - `isolation_level`: the isolation level for the transaction (e.g., "SERIALIZABLE").
        - `commit`: if `True`, the method performs a commit after execution.
        """

        def decorator(method):
            @wraps(method)
            async def wrapper(*args, **kwargs):
                async with self.session_maker() as session:
                    try:
                        if isolation_level:
                            await session.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"))

                        result = await method(*args, session=session, **kwargs)

                        if commit:
                            await session.commit()

                        return result
                    except Exception as e:
                        await session.rollback()
                        logger.error(f"Error during transaction execution: {e}")
                        raise
                    finally:
                        await session.close()

            return wrapper

        return decorator

    @property
    def session_dependency(self) -> Callable:
        """Returns a FastAPI dependency providing access to a session without a transaction."""
        return Depends(self.get_session)

    @property
    def transaction_session_dependency(self) -> Callable:
        """Returns a FastAPI dependency providing access to a session with transaction support."""
        return Depends(self.get_transaction_session)


# Initialize the database session manager
session_manager = DatabaseSessionManager(async_session_maker)

# FastAPI dependencies for using sessions
SessionDep = session_manager.session_dependency
TransactionSessionDep = session_manager.transaction_session_dependency

# Example usage of the decorator
# @session_manager.connection(isolation_level="SERIALIZABLE", commit=True)
# async def example_method(*args, session: AsyncSession, **kwargs):
#     # Method logic
#     pass


# Example usage of a dependency
# @router.post("/register/")
# async def register_user(user_data: SUserRegister, session: AsyncSession = TransactionSessionDep):
#     # Endpoint logic
#     pass
