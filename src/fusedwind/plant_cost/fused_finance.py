# KLD: _cost model for FUSED_Wind - most basic structure

from openmdao.lib.datatypes.api import Float, Int, Array, VarTree
from openmdao.main.api import Component, Assembly, VariableTree

from fusedwind.plant_flow.asym import BaseAEPModel
from fusedwind.plant_cost.fused_bos_costs import BaseBOSCostModel, BOSVarTree, ExtendedBOSCostModel
from fusedwind.plant_cost.fused_opex import BaseOPEXModel, OPEXVarTree, ExtendedOPEXModel
from fusedwind.plant_cost.fused_tcc import BaseTurbineCostModel, FullTurbineCostModel
from fusedwind.interface import base, implement_base

#########################################################################
# Financial models

# Base Financial Model
@base
class BaseFinancialAggregator(Component):
    """ Base financial aggregator for doing some auxiliary cost calculations needed to get a full wind plant cost of energy estimate.    """

    # Inputs
    turbine_cost = Float(iotype='in', desc = 'A Wind Turbine Capital _cost')
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')
    bos_costs = Float(iotype='in', desc='A Wind Plant Balance of Station _cost Model')
    avg_annual_opex = Float(iotype='in', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='in', desc='A Wind Plant Annual Energy Production Model', units='kW*h')

    #Outputs
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')

@base
class BaseFinancialModel(Assembly):
    """ Base financial assembly for coupling models to get a full wind plant cost of energy estimate.    """

    # Inputs
    turbine_cost = Float(iotype='in', desc = 'A Wind Turbine Capital _cost')
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')
    bos_costs = Float(iotype='in', desc='A Wind Plant Balance of Station _cost Model')
    avg_annual_opex = Float(iotype='in', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='in', desc='A Wind Plant Annual Energy Production Model', units='kW*h')

    #Outputs
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')

def configure_base_finance(assembly):
    """ Base configure method for a financial assembly for coupling models to get a full wind plant cost of energy estimate.  It adds a default financial aggregator component.    """

    assembly.add('fin', BaseFinancialAggregator())

    assembly.driver.workflow.add(['fin'])

    assembly.connect('turbine_cost','fin.turbine_cost')
    assembly.connect('turbine_number', 'fin.turbine_number')
    assembly.connect('bos_costs', 'fin.bos_costs')
    assembly.connect('avg_annual_opex', 'fin.avg_annual_opex')
    assembly.connect('net_aep', 'fin.net_aep')

    assembly.connect('fin.coe','coe')

# Ignoring more detailed financial model structures for now

#########################################################################
# Implementation assembly shells

# Main financial assembly
@base
class BaseFinancialAnalysis(Assembly):
    """ Base financial analysis assembly for coupling models to get a full wind plant cost of energy estimate.    """

    # Inputs
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')

    #Outputs
    turbine_cost = Float(iotype='out', desc = 'A Wind Turbine Capital _cost')
    bos_costs = Float(iotype='out', desc='A Wind Plant Balance of Station _cost Model')
    avg_annual_opex = Float(iotype='out', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='out', desc='A Wind Plant Annual Energy Production Model', units='kW*h')
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')

def configure_base_financial_analysis(assembly):
    """ Base configure method for a financial analysis assembly for coupling models to get a full wind plant cost of energy estimate.  It adds a default financial aggregator component as well as base cost models for each major financial sub-model.    """

    # To be replaced by actual models
    assembly.add('tcc_a',BaseTurbineCostModel())
    assembly.add('bos_a',BaseBOSCostModel())
    assembly.add('opex_a',BaseOPEXModel())
    assembly.add('aep_a',BaseAEPModel())
    assembly.add('fin_a',BaseFinancialModel())

    assembly.driver.workflow.add(['tcc_a','bos_a','opex_a','aep_a','fin_a'])

    assembly.connect('tcc_a.turbine_cost',['fin_a.turbine_cost'])
    assembly.connect('bos_a.bos_costs','fin_a.bos_costs')
    assembly.connect('opex_a.avg_annual_opex','fin_a.avg_annual_opex')
    assembly.connect('aep_a.net_aep','fin_a.net_aep')
    assembly.connect('turbine_number','fin_a.turbine_number')

    # Connect outputs
    assembly.connect('aep_a.net_aep','net_aep')
    assembly.connect('opex_a.avg_annual_opex','avg_annual_opex')
    assembly.connect('bos_a.bos_costs','bos_costs')
    assembly.connect('tcc_a.turbine_cost','turbine_cost')
    assembly.connect('fin_a.coe','coe')

@implement_base(BaseFinancialAnalysis)
class ExtendedFinancialAnalysis(Assembly):
    """ Extended financial analysis assembly for coupling models to get a full wind plant cost of energy estimate as well as provides a detailed cost breakdown for the plant.    """

    # Inputs
    turbine_number = Int(iotype = 'in', desc = 'number of turbines at plant')

    #Outputs
    turbine_cost = Float(iotype='out', desc = 'A Wind Turbine Capital _cost')
    bos_costs = Float(iotype='out', desc='A Wind Plant Balance of Station _cost Model')
    avg_annual_opex = Float(iotype='out', desc='A Wind Plant Operations Expenditures Model')
    net_aep = Float(iotype='out', desc='A Wind Plant Annual Energy Production Model', units='kW*h')
    coe = Float(iotype='out', desc='Levelized cost of energy for the wind plant')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')
    bos_breakdown = VarTree(BOSVarTree(), iotype='out', desc='BOS cost breakdown')

def configure_extended_financial_analysis(assembly):
    """ Extended configure method for a financial assembly for coupling models to get a full wind plant cost of energy estimate.  It replaces the base cost models with their extended versions for balance of station cost and operational expenditures.   """

    configure_base_financial_analysis(assembly)

    # To be replaced by actual models
    #assembly.replace('tcc',FullTurbineCostModel())
    assembly.replace('bos_a',ExtendedBOSCostModel())
    assembly.replace('opex_a',ExtendedOPEXModel())

    assembly.connect('opex_a.opex_breakdown', 'opex_breakdown')
    assembly.connect('bos_a.bos_breakdown', 'bos_breakdown')
