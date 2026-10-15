"""Workflow de veille immobilière — maisons, Lyon ouest et alentours, ~800 000 €."""

from datetime import date

from pydantic import BaseModel

import mistralai.workflows as workflows
from mistralai import Mistral

CRITERES = """MES CRITÈRES :
- Zone : Lyon et alentours (Lyon 5e/6e/9e, Tassin-la-Demi-Lune, Écully, Saint-Cyr-au-Mont-d'Or,
  Francheville, Saint-Didier-au-Mont-d'Or, Limonest, Dardilly, Champagne-au-Mont-d'Or, Caluire,
  et autres communes de la couronne ouest lyonnaise)
- Type : MAISON uniquement
- Budget : 550 000 – 850 000 € (cible ~800 000 €)
- Surface : minimum 100 m²
- Pièces : 4 minimum
- Souhaité : extérieur (jardin/terrasse), garage, DPE C ou mieux
- Exclusions : viager, travaux lourds, copropriété, terrains nus"""

SYSTEM_PROMPT = f"""Tu es mon agent de veille immobilière personnel.

{CRITERES}

TA MISSION :
1. Cherche sur les portails (SeLoger, Leboncoin, PAP, Logic-Immo, sites d'agences locales
   lyonnaises) les annonces correspondant à MES CRITÈRES, en insistant sur les annonces
   récentes ou fraîchement republiées.
2. Pour chaque annonce retenue, donne : prix, surface, nombre de pièces, commune,
   lien de l'annonce, points forts, points de vigilance (DPE, charges, surface du terrain).
3. Signale les annonces dont le prix a baissé si l'information est visible.
4. Si aucune annonce ne correspond, dis-le franchement plutôt que de proposer des
   biens hors critères.
5. Réponds toujours en français, en liste d'annonces numérotées, du plus intéressant
   au moins intéressant."""


class VeilleImmoInput(BaseModel):
    """Entrée de la veille : rien de requis, le schedule passe une date optionnelle."""
    date: str = ""


@workflows.activity()
async def chercher_annonces() -> str:
    """Recherche sur le web les annonces correspondant aux critères."""
    client = Mistral()  # MISTRAL_API_KEY lu depuis l'environnement
    response = client.chat.complete(
        model="mistral-medium-latest",
        messages=[
            {
                "role": "user",
                "content": "Lance la veille immobilière du jour : trouve les annonces "
                           "correspondant à mes critères.",
            }
        ],
        tools=[{"type": "web_search"}],
    )
    return response.choices[0].message.content or "Aucun résultat."


@workflows.workflow.define(
    name="veille-immo-lyon",
    workflow_display_name="Veille Immo Lyon",
    workflow_description="Veille quotidienne des annonces de maisons à Lyon ouest et "
                         "alentours, budget ~800 000 €.",
)
class VeilleImmoWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, input: VeilleImmoInput) -> str:
        digest = await chercher_annonces()
        header = f"🏠 Veille immobilière du {input.date or date.today().isoformat()}\n\n"
        return header + digest
