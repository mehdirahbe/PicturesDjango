class CFicheDias
{
public:
	CFicheDias()
	{
		m_nRangee=m_nNumero=1;
		m_bAgrandi=m_bClasse=m_bVerifie=false;
		m_Date = _T("01/01/1995");
		m_Boite = _T("v1");
		m_bCameraDigitale=false;
	}

	CFicheDias(const CFicheDias &Autre)
	{
		*this=Autre;
	}
	
	virtual ~CFicheDias() {}
	
	bool operator==(const CFicheDias &Autre) const
	{
		return(
		m_Sujet==Autre.m_Sujet &&
		m_Date==Autre.m_Date &&
		m_Boite==Autre.m_Boite &&
		m_nRangee==Autre.m_nRangee &&
		m_nNumero==Autre.m_nNumero &&
		m_SujetDias==Autre.m_SujetDias &&
		m_bAgrandi==Autre.m_bAgrandi &&
		m_bClasse==Autre.m_bClasse &&
		m_bVerifie==Autre.m_bVerifie &&
		m_Commentaire==Autre.m_Commentaire &&
		m_bCameraDigitale==Autre.m_bCameraDigitale &&
		m_PremierNiveau==Autre.m_PremierNiveau &&
		m_SecondNiveau==Autre.m_SecondNiveau &&
		m_TroisiemeNiveau==Autre.m_TroisiemeNiveau &&
		m_NomFichierJpeg==Autre.m_NomFichierJpeg);
	}

	const CFicheDias &operator=(const CFicheDias &Autre)
	{
		m_Sujet=Autre.m_Sujet;
		m_Date=Autre.m_Date;
		m_Boite=Autre.m_Boite;
		m_nRangee=Autre.m_nRangee;
		m_nNumero=Autre.m_nNumero;
		m_SujetDias=Autre.m_SujetDias;
		m_bAgrandi=Autre.m_bAgrandi;
		m_bClasse=Autre.m_bClasse;
		m_bVerifie=Autre.m_bVerifie;
		m_Commentaire=Autre.m_Commentaire;
		m_bCameraDigitale=Autre.m_bCameraDigitale;
		m_PremierNiveau=Autre.m_PremierNiveau;
		m_SecondNiveau=Autre.m_SecondNiveau;
		m_TroisiemeNiveau=Autre.m_TroisiemeNiveau;
		m_NomFichierJpeg=Autre.m_NomFichierJpeg;
		return *this;
	}

	CString	m_Sujet;
	CString	m_Date;
	CString	m_Boite;
	unsigned	m_nRangee;
	//Numéro de la rangée si dias, du raw si digital
	unsigned	m_nNumero;
	CString	m_SujetDias;
	BOOL	m_bAgrandi;
	BOOL	m_bClasse;
	BOOL	m_bVerifie;
	CString	m_Commentaire;
	/*Vrai si ça vient d'une caméra digitale,
	boîte, rangée doivent alors être ignorés*/
	BOOL m_bCameraDigitale;
	//Premier niveau de répertoire pour retrouver les fichiers
	CString m_PremierNiveau;
	//Deuxième niveau de répertoire pour retrouver les fichiers
	CString m_SecondNiveau;
	//Troisième niveau de répertoire pour retrouver les fichiers
	CString m_TroisiemeNiveau;
	//Nom du fichier (optionel, si vide, c'est le n° m_nNumero en %03d)
	CString m_NomFichierJpeg;
};


class CBanqueDias {
public:
	CBanqueDias() {}
	virtual ~CBanqueDias() {}

	int LitBanque(LPCTSTR pszNomFich);
	int SauveBanque(LPCTSTR pszNomFich);
	int GetTaille() {return m_Dias.GetSize();}
	int CreeFiche(int bTakeLast=1);
	int InsereFiche(int nIndex,int bTakeLast=1);
	int CorrespondsCritere(int nNoFiche,CString *pValChamp,int nChamp[3]);

	CArray <CFicheDias,CFicheDias> m_Dias;
};

