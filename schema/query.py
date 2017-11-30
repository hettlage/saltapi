from schema.partner import *
from schema.selectors import Selectors
from schema.proposal import *
from data.proposal import get_proposals
from data.partner import get_partners
from data.targets import get_targets
from data.selectors import get_selectors_data
from schema.instruments import *
import graphene
from graphene import Field, List, String


class Query(graphene.ObjectType):
    proposals = Field(List(Proposals), semester=String(), partner_code=String(), proposal_code=String(),
                      description="List of proposals per semester. Can be reduced to per partner or per proposal. " 
                                  " Semester must be provided in all cases"
                      )
    targets = Field(List(Target), semester=String(), partner_code=String(), proposal_code=String(),
                    description="List of targets per semester can be reduced to per partner or per proposal. " 
                                " Semester must be provided in all cases")
    partners_allocations = Field(List(PartnersAllocations), semester=String(), partner_code=String(),
                                 description="List of all allocations of SALT Partners")
    selectors = Field(Selectors)

    def resolve_proposals(self, context, info, args, partner_code=None, proposal_code=None):
        if 'partner_code' in context:
            partner_code = context['partner_code']

        if 'proposal_code' in context:
            proposal_code = context['proposal_code']
        return get_proposals(semester=context['semester'], partner_code=partner_code, proposal_code=proposal_code)

    def resolve_targets(self, context, info, args, partner_code=None, proposal_code=None):
        if 'partner_code' in context:
            partner_code = context['partner_code']

        if 'proposal_code' in context:
            proposal_code = context['proposal_code']

        return get_targets(semester=context['semester'], partner_code=partner_code, proposal_code=proposal_code)

    def resolve_partners_allocations(self, context, info, args, partner_code=None, semester=None):
        if 'partner_code' in context:
            partner_code = context['partner_code']

        if 'semester' in context:
            semester = context['semester']

        return get_partners(semester=semester, partner_code=partner_code)

    def resolve_selectors(self, context, info, args):
        return get_selectors_data()


schema = graphene.Schema(query=Query, types=[HRS, RSS, BVIT, SCAM])
