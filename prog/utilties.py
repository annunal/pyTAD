import os,requests
            if useget:
                    resp=requests.get(url)
                    resp=resp.text
            else:
                #resp=urlopen(url)
                #resp = resp.read().decode("utf-8")
                print(url)
                with urlopen(url) as response:
                    resp = response.read().decode("utf-8")
                
        except:
            return ''
        if usecacheIfPresent:
            with open(fname,'w',encoding='utf-8') as f:
                f.write(resp)
    return resp