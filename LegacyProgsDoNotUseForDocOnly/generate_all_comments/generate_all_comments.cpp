// generate_all_comments.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "strsafe.h"

typedef std::map<std::string,std::string> CStrStrMap;

/*Used to sort strings without accents or case*/
class CStringSort:public std::binary_function<std::string, std::string, bool>
{
public:
    bool operator()(const std::string& x, const std::string& y) const
	{
		//Strip accents
		std::string l_First(x),l_Second(y);
		StripAccents(l_First);
		StripAccents(l_Second);

		return _stricmp(l_First.c_str(),l_Second.c_str())<0;
	}
private:
	void StripAccents(std::string &l_Text) const;
};

void CStringSort::StripAccents(std::string &l_Text) const
{
	for (std::string::iterator l_it=l_Text.begin();l_it!=l_Text.end();++l_it)
	{
		if (*l_it=='é' || *l_it=='è')
			*l_it='e';
		if (*l_it=='û')
			*l_it='u';
	}
}

typedef std::map<std::string,int,CStringSort> CStrIntMap;

/*Used to sort titiles as much as possible by date*/
class CHTMLTitleSort:public std::binary_function<std::string, std::string, bool>
{
public:
	CHTMLTitleSort()
	{
		m_AllMonths.insert(CStrIntMap::value_type("janvier",1));
		m_AllMonths.insert(CStrIntMap::value_type("fevrier",2));
		m_AllMonths.insert(CStrIntMap::value_type("mars",3));
		m_AllMonths.insert(CStrIntMap::value_type("avril",4));
		m_AllMonths.insert(CStrIntMap::value_type("mai",5));
		m_AllMonths.insert(CStrIntMap::value_type("juin",6));
		m_AllMonths.insert(CStrIntMap::value_type("juillet",7));
		m_AllMonths.insert(CStrIntMap::value_type("aout",8));
		m_AllMonths.insert(CStrIntMap::value_type("septembre",9));
		m_AllMonths.insert(CStrIntMap::value_type("octobre",10));
		m_AllMonths.insert(CStrIntMap::value_type("novembre",11));
		m_AllMonths.insert(CStrIntMap::value_type("decembre",12));
	}

    bool operator()(const std::string& x, const std::string& y) const
	{
		//Split in words
		GetAllWords(m_AllWordsFirst,x);
		GetAllWords(m_AllWordsSecond,y);
		int l_nFirst=GetDate(m_AllWordsFirst);
		int l_nSecond=GetDate(m_AllWordsSecond);
		if (l_nFirst<l_nSecond)
			return true;
		else if (l_nFirst==l_nSecond && x<y)
			return true;
		else
			return false;
	}
private:
	//Split the string into the words
	void GetAllWords(std::vector<std::string> &p_AllWords,const std::string& p_ToSplit) const;
	//Return the date YYYYMMDD
	int GetDate(const std::vector<std::string> &p_AllWords) const;
	//List of words
	mutable std::vector<std::string> m_AllWordsFirst;
	mutable std::vector<std::string> m_AllWordsSecond;
	//All months, case and accents insensitive
	CStrIntMap m_AllMonths;
};

//Return the date YYYYMMDD
int CHTMLTitleSort::GetDate(const std::vector<std::string> &p_AllWords) const
{
	int l_nYear=0;
	int l_nMonth=0;
	int l_nDay=0;
	for (std::vector<std::string>::const_iterator l_it=p_AllWords.begin();l_it!=p_AllWords.end();++l_it)
	{
		//Is it a year (4 or 2 digits) ?
		int l_nVal=atoi(l_it->c_str());
		if (l_nVal>1900 && l_nVal<2100)
			l_nYear=l_nVal;
		else if (l_nVal>60 && l_nVal<=99)
			l_nYear=l_nVal+1900;
		else
		{
			//A month ?
			CStrIntMap::const_iterator l_Month=m_AllMonths.find(*l_it);

			if (l_Month!=m_AllMonths.end())
			{
				l_nMonth=l_Month->second;

				//Maybe the previous item is a day ?
				if (l_it>p_AllWords.begin())
				{
					std::vector<std::string>::const_iterator l_Prev=l_it;
					l_Prev--;

					l_nDay=atoi(l_Prev->c_str());
				}
			}
		}
	}

	return l_nYear*10000+l_nMonth*100+l_nDay;
}

//Split the string into the words
void CHTMLTitleSort::GetAllWords(std::vector<std::string> &p_AllWords,const std::string& p_ToSplit) const
{
	p_AllWords.resize(0);
	
	std::vector<char> l_WorkBuf(p_ToSplit.length()+1);
	char *l_pszWorkBuf=&l_WorkBuf[0];
	StringCchCopy(l_pszWorkBuf,p_ToSplit.length()+1,p_ToSplit.c_str());

	while (true)
	{
		char *l_pszWord=strtok(l_pszWorkBuf," \t(),;/.:");
		l_pszWorkBuf=NULL;
		if (l_pszWord)
			p_AllWords.push_back(l_pszWord);
		else
			break;
	}
}


//Title is the key, value is the file
typedef std::map<std::string,std::string,CHTMLTitleSort> CHTMLTitle;

class CHTMLFile
{
public:
	std::string m_Header;
	CHTMLTitle m_Links;
};

typedef std::map<std::string,CHTMLFile> CStrHTMLMap;

void GetDisplayNamesOfDirs(CStrStrMap &p_TheMap)
{
	std::string l_BelgiqueDir("belgique");
	std::string l_BelgiqueDisplay("Belgique ");

	p_TheMap.clear();
	p_TheMap.insert(CStrStrMap::value_type("belgique","Belgique"));
	p_TheMap.insert(CStrStrMap::value_type("cecile","Cécile"));
	p_TheMap.insert(CStrStrMap::value_type("collegues_amis","Collègues et amis"));
	p_TheMap.insert(CStrStrMap::value_type("famille","Famille"));
	p_TheMap.insert(CStrStrMap::value_type("mehdi","Mehdi"));
	p_TheMap.insert(CStrStrMap::value_type("voyages","Voyages"));
	for (int l_nYear=2003;l_nYear<2060;l_nYear++)
	{
		char l_szYear[10];

		_itoa_s(l_nYear,l_szYear,sizeof(l_szYear),10);
		p_TheMap.insert(CStrStrMap::value_type(l_BelgiqueDir+l_szYear,l_BelgiqueDisplay+l_szYear));
		p_TheMap.insert(CStrStrMap::value_type(l_szYear,l_szYear));
	}
	p_TheMap.insert(CStrStrMap::value_type("dias","Dias"));
}

void SplitPath(std::list<std::string> &p_PathParts,const std::string &p_Path)
{
	p_PathParts.clear();

	int l_nLastSlashPos;
	std::string l_Path(p_Path);
	while ((l_nLastSlashPos=l_Path.find_last_of("\\/"))>=0)
	{
		std::string l_ToAdd(l_Path.substr(l_nLastSlashPos+1,l_Path.length()-l_nLastSlashPos));
		p_PathParts.push_front(l_ToAdd);
		l_Path=l_Path.substr(0,l_nLastSlashPos);
	}
}

std::string GetDisplayNamesOfDir(const CStrStrMap &p_TheMap,const char *l_pszTheDir)
{
	CStrStrMap::const_iterator l_Found=p_TheMap.find(l_pszTheDir);

	if (l_Found!=p_TheMap.end())
		return l_Found->second;
	else
		return l_pszTheDir;
}

void FillAddtionalLinks(CStrStrMap &p_DirNames,const std::string &p_Path,CHTMLFile &p_AFile,const CStrHTMLMap &p_Files)
{
	//Get html file dir
	int l_nLastSlash=p_Path.find_last_of("\\/");
	if (l_nLastSlash<=0)
		return;

	std::string l_Dir=p_Path.substr(0,l_nLastSlash);
	for (CStrHTMLMap::const_iterator l_it=p_Files.begin();l_it!=p_Files.end();++l_it)
	{
		const std::string &l_Path=l_it->first;

		if (l_Path==p_Path)
			continue;
		if (strncmp(l_Path.c_str(),l_Dir.c_str(),l_Dir.length())==0)
		{
			//The is a level after p_Path-->add it in the links 
			std::string l_NextDir=l_Path.substr(l_Dir.length()+1);
			l_nLastSlash=l_NextDir.find_last_of("\\/");
			if (l_nLastSlash>=0)
				l_NextDir=l_NextDir.substr(0,l_nLastSlash);
			std::string l_Title=GetDisplayNamesOfDir(p_DirNames,l_NextDir.c_str());
			p_AFile.m_Links.insert(CStrStrMap::value_type(l_Title,l_NextDir+"/index.html"));
		}
	}

}

std::string GetUserProfile(char *envp[])
{
	const char *l_pszUSERPROFILE="USERPROFILE=";
	int l_nUSERPROFILE=strlen(l_pszUSERPROFILE);
	while (*envp)
	{
		const char *l_pszEnvVar=*envp++;
		if (_strnicmp(l_pszUSERPROFILE,l_pszEnvVar,l_nUSERPROFILE)==0)
			return l_pszEnvVar+l_nUSERPROFILE;
	}
	return "";
}

void GetAllFiles(const char *pszCmdLine,std::vector<std::string> &p_Allbatches)
{
	FILE *l_hf=_popen(pszCmdLine,"rt");
	
	if (l_hf)
	{
		p_Allbatches.reserve(100);
		
		char l_szLine[1024];
		while (fgets(l_szLine,sizeof(l_szLine),l_hf))
		{
			char *l_pszEnd=strchr(l_szLine,'\n');
			if (l_pszEnd)
				*l_pszEnd=0;
			if (*l_szLine)
				p_Allbatches.push_back(l_szLine);
		}
		_pclose(l_hf);
	}
}

std::string GetTitleFromBatch(const std::string &p_BatchPath)
{
	FILE *l_hf=NULL;
	fopen_s(&l_hf,p_BatchPath.c_str(),"rt");
	if (!l_hf)
	{
		printf("Cannot open %s\n",p_BatchPath.c_str());
		return "";
	}
	std::vector<char> l_buf(_filelength(_fileno(l_hf))+1);
	char *l_pszBuf=&l_buf[0];
	fgets(l_pszBuf,l_buf.size(),l_hf);
	fclose(l_hf);

	//Parse the line
	char *l_pszLastQuote=strrchr(l_pszBuf,'\"');
	if (!l_pszLastQuote)
		return "";
	*l_pszLastQuote=0;
	char *l_pszFirstQuote=strrchr(l_pszBuf,'\"');
	if (!l_pszFirstQuote)
		return "";

	std::string l_Result=l_pszFirstQuote+1;
	std::string::iterator l_it=l_Result.begin();
	for (l_it++;l_it!=l_Result.end();++l_it)
	{
		std::string::iterator l_PrevIt=l_it;
		l_PrevIt--;
		if (*l_PrevIt>=0 && *l_it>=0 && (!(isspace(*l_PrevIt) || ispunct(*l_PrevIt)) && isupper(*l_it)))
			*l_it=tolower(*l_it);
	}
	return l_Result;
}

void GenerateIndexHtml(const std::vector<std::string> &p_Allbatches,const std::string &p_DiasPath)
{
	CStrStrMap l_DirNames;
	GetDisplayNamesOfDirs(l_DirNames);
	CStrHTMLMap l_Files;
	std::list<std::string> l_PathParts;

	{
		for (std::vector<std::string>::const_iterator l_it=p_Allbatches.begin();l_it!=p_Allbatches.end();++l_it)
		{
			std::string l_ParentDir=*l_it;
			int l_LastSlash=l_ParentDir.find_last_of("\\/");
			if (l_LastSlash>0)
			{
				l_ParentDir=l_ParentDir.substr(0,l_LastSlash);
				l_LastSlash=l_ParentDir.find_last_of("\\/");
				if (l_LastSlash>0)
				{
					l_ParentDir=l_ParentDir.substr(0,l_LastSlash+1);
					std::string l_FilePath=l_ParentDir+"index.html";

					//Nouveau fichier
					CStrHTMLMap::iterator l_File=l_Files.find(l_FilePath);
					SplitPath(l_PathParts,l_FilePath.substr(p_DiasPath.length()-1));
					if (l_File==l_Files.end())
					{
						l_Files.insert(CStrHTMLMap::value_type(l_FilePath,CHTMLFile()));
						l_File=l_Files.find(l_FilePath);
						std::string &l_HTMLHeader=l_File->second.m_Header;
						
						l_HTMLHeader.reserve(500);
						l_HTMLHeader="<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Strict//EN\">\n<html>\n<head>\n\t<link TYPE=\"text/css\" REL=\"STYLESHEET\" HREF=\"";

						//From the file, where is the css ?
						std::list<std::string>::const_iterator l_itParts=l_PathParts.end();
						for (l_itParts--;l_itParts!=l_PathParts.begin();--l_itParts)
							l_HTMLHeader+="../";
						l_HTMLHeader+="dias.css\">\n\t<title>";

						std::list<std::string>::const_iterator l_itLastDir=l_PathParts.end();
						l_itLastDir--;	//Go to last element: the file
						l_itLastDir--;	//Go to last dir part

						std::string l_DirDisplayName=GetDisplayNamesOfDir(l_DirNames,l_itLastDir->c_str());
						l_HTMLHeader+=l_DirDisplayName;
						l_HTMLHeader+="</title>\n\t<meta name=\"author\" content=\"Mehdi Rahman\">\n\t<meta name=\"description\" content=\"";
						l_HTMLHeader+=l_DirDisplayName;
						l_HTMLHeader+="\">\n</head>\n<body>\n";
					}

					//Add the link with the display name
					SplitPath(l_PathParts,*l_it);
					std::list<std::string>::const_iterator l_itLastDir=l_PathParts.end();
					l_itLastDir--;	//Go to last element: the file
					l_itLastDir--;	//Go to last dir part

					l_File->second.m_Links.insert(CStrStrMap::value_type(GetTitleFromBatch(*l_it),*l_itLastDir+"/planchecontact.html"));
				}
			}
		}
	}

	//Finish and save each html
	{
		for (CStrHTMLMap::iterator l_it=l_Files.begin();l_it!=l_Files.end();++l_it)
		{
			FILE *hf=NULL;
			fopen_s(&hf,l_it->first.c_str(),"wt");
			if (hf)
			{
				FillAddtionalLinks(l_DirNames,l_it->first,l_it->second,l_Files);
				fprintf(hf,"%s",l_it->second.m_Header.c_str());
				for (CHTMLTitle::const_iterator l_itLinks=l_it->second.m_Links.begin();l_itLinks!=l_it->second.m_Links.end();++l_itLinks)
				{
					fprintf(hf,"\t<a href=\"%s\">%s</a><br>\n",l_itLinks->second.c_str(),l_itLinks->first.c_str());
				}
				fprintf(hf,"\t<a href=\"../index.html\">Retour</a>\n</body>\n</html>\n");
				fclose(hf);
			}
			else
				printf("Cannot save %s\n",l_it->first.c_str());
		}
	}
}

int main(int argc, char* argv[],char *envp[])
{
	if (argc<2)
	{
		printf("Chemin des dias requis, incapable de trouver ou sont les dias\n");
		return -1;
	}
	std::string l_DiasPath=argv[1];

	if (*l_DiasPath.rbegin()!='\\' && *l_DiasPath.rbegin()!='/')
		l_DiasPath+="\\";
	
	//Enumère tous les fichiers
	std::string l_Liste=std::string("dir /s /b \"")+l_DiasPath+"preparehtml.bat\"";
	std::vector<std::string> l_Allbatches;
	GetAllFiles(l_Liste.c_str(),l_Allbatches);
	
	//Les exécute
	//2017: Old code, does it still have a meaning to regenerate all?
	//If ever it should be reactivated, args must be passed properly, see CAccessDiasDlg::OnOutilsCreeCommentHtml
	/*_chdir(l_DiasPath.c_str());
	for (std::vector<std::string>::const_iterator l_it=l_Allbatches.begin();l_it!=l_Allbatches.end();++l_it)
	{
		std::string l_Command=std::string("\"")+*l_it+"\"";
		system(l_Command.c_str());
	}*/
	
	//Génère les fichiers html
	GenerateIndexHtml(l_Allbatches,l_DiasPath);
	
	return 0;
}

