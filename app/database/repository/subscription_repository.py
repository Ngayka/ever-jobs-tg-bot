from sqlalchemy import select

from app.database.session import async_session_factory
from app.database.models import JobSubscription


class SubscriptionRepository:
    async def create_or_get(
        self,
        *,
        telegram_user_id: int,
        search_term: str,
        source_group: str,
        location: str | None = None,
    ) -> JobSubscription:
        async with async_session_factory() as session:
            statement = select(JobSubscription).where(
                JobSubscription.telegram_user_id
                == telegram_user_id,
                JobSubscription.search_term
                == search_term,
                JobSubscription.source_group
                == source_group,
                JobSubscription.location
                == location,
            )

            result = await session.execute(statement)
            subscription = result.scalar_one_or_none()

            if subscription is not None:
                if not subscription.enabled:
                    subscription.enabled = True
                    await session.commit()
                    await session.refresh(subscription)

                return subscription

            subscription = JobSubscription(
                telegram_user_id=telegram_user_id,
                search_term=search_term,
                source_group=source_group,
                location = location,
                enabled=True,
            )

            session.add(subscription)

            await session.commit()
            await session.refresh(subscription)

            return subscription

    async def get_enabled(
        self,
    ) -> list[JobSubscription]:
        async with async_session_factory() as session:
            statement = select(JobSubscription).where(
                JobSubscription.enabled.is_(True)
            ).order_by(JobSubscription.id.asc())

            result = await session.execute(statement)

            return list(
                result.scalars().all()
            )

    async def get_user_subscriptions(
        self,
        *,
        telegram_user_id: int,
        enabled_only: bool = False,
    ) -> list[JobSubscription]:
        async with async_session_factory() as session:
            statement = select(JobSubscription).where(
                JobSubscription.telegram_user_id
                == telegram_user_id,
            )

            if enabled_only:
                statement = statement.where(
                    JobSubscription.enabled.is_(True)
                )

            statement = statement.order_by(
                JobSubscription.id.desc()
            )

            result = await session.execute(statement)

            return list(
                result.scalars().all()
            )

    async def get_by_id(
        self,
        *,
        subscription_id: int,
        telegram_user_id: int,
    ) -> JobSubscription | None:
        async with async_session_factory() as session:
            statement = select(JobSubscription).where(
                JobSubscription.id
                == subscription_id,
                JobSubscription.telegram_user_id
                == telegram_user_id,
            )

            result = await session.execute(statement)

            return result.scalar_one_or_none()

    async def disable(
        self,
        *,
        subscription_id: int,
        telegram_user_id: int,
    ) -> bool:
        async with async_session_factory() as session:
            statement = select(JobSubscription).where(
                JobSubscription.id
                == subscription_id,
                JobSubscription.telegram_user_id
                == telegram_user_id,
            )

            result = await session.execute(statement)
            subscription = result.scalar_one_or_none()

            if subscription is None:
                return False

            subscription.enabled = False

            await session.commit()

            return True

    async def enable(
            self,
            *,
            subscription_id: int,
            telegram_user_id: int,
    ) -> JobSubscription | None:
        async with async_session_factory() as session:
            statement = select(JobSubscription).where(
                JobSubscription.id
                == subscription_id,
                JobSubscription.telegram_user_id
                == telegram_user_id,
            )

            result = await session.execute(statement)

            subscription = result.scalar_one_or_none()

            if subscription is None:
                return None

            subscription.enabled = True

            await session.commit()
            await session.refresh(subscription)

            return subscription

subscription_repository = SubscriptionRepository()