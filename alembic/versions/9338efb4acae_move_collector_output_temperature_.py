"""Move collector output temperature setpoint to temperatures parameters

Revision ID: 9338efb4acae
Revises: e70c05e7d2d5
Create Date: 2026-06-15 12:53:16.928971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision: str = '9338efb4acae'
down_revision: Union[str, None] = 'e70c05e7d2d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    import copy
    import sqlalchemy.orm as orm
    import sqlalchemy.orm.session as sess

    Base = orm.declarative_base()

    class Simulation(Base):
        __tablename__ = "simulation"
        id = sa.Column(sa.String, primary_key=True, nullable=False)
        parameters = sa.Column(sa.JSON)

    statement = sa.select(Simulation)

    with sess.Session(bind=op.get_bind()) as session:
        simulations = session.scalars(statement)

        for simulation in simulations:
            parameters = copy.deepcopy(simulation.parameters)
            
            values = parameters.get("values", {})
            collector_field = values.get("collector_field", {})
            
            if "output_temperature_setpoint_degC" in collector_field:
                temp_setpoint = collector_field.pop("output_temperature_setpoint_degC")
                
                temperatures = values.get("temperatures", {})
                if not isinstance(temperatures, dict):
                    temperatures = {}
                
                temperatures["output_temperature_setpoint_degC"] = temp_setpoint
                values["temperatures"] = temperatures
                
                simulation.parameters = parameters
        
        session.commit()


def downgrade() -> None:
    import copy
    import sqlalchemy.orm as orm
    import sqlalchemy.orm.session as sess

    Base = orm.declarative_base()

    class Simulation(Base):
        __tablename__ = "simulation"
        id = sa.Column(sa.String, primary_key=True, nullable=False)
        parameters = sa.Column(sa.JSON)

    statement = sa.select(Simulation)

    with sess.Session(bind=op.get_bind()) as session:
        simulations = session.scalars(statement)

        for simulation in simulations:
            parameters = copy.deepcopy(simulation.parameters)
            
            values = parameters.get("values", {})
            temperatures = values.get("temperatures", {})
            
            if isinstance(temperatures, dict) and "output_temperature_setpoint_degC" in temperatures:
                temp_setpoint = temperatures.pop("output_temperature_setpoint_degC")
                
                collector_field = values.get("collector_field", {})
                if not isinstance(collector_field, dict):
                    collector_field = {}
                
                collector_field["output_temperature_setpoint_degC"] = temp_setpoint
                values["collector_field"] = collector_field
                
                simulation.parameters = parameters
        
        session.commit()
