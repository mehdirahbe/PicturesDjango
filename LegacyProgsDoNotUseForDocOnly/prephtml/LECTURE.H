#define UINT unsigned
#define BOOL int

struct CFicheDias
{
	CFicheDias()
	{
		memset(this,0,sizeof(*this));
	}
	char	m_Sujet[200];
	char	m_Date[50];
	char	m_Boite[20];
	UINT	m_nRangee;
	UINT	m_nNumero;
	char	m_SujetDias[500];
	BOOL	m_bAgrandi;
	BOOL	m_bClasse;
	BOOL	m_bVerifie;
	char	m_Commentaire[1000];
	BOOL	m_bCameraDigitale;
	char	m_PremierNiveau[200];
	char	m_SecondNiveau[200];
	char	m_TroisiemeNiveau[200];
	char	m_NomFichier[200];
};
