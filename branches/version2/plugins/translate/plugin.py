# Google translate
'''Translate plugin. !translate en:en translated phrase will translate the phrase from the first two letter language code to the second one. !translate list will list the languages available and their two letter code.'''
import re
import lib.webbot as webbot

'''
    # trans
    # google translation -(www.google.com\translate_t?)
    # -speechless supplied
    #
    proc trans {input} {
      global incithcharset
      ; set results 0 ; set output ""; set match "" ; set titem ""

      # if we don't want any search results, stop now.
      if {$incith::google::trans_results <= 0} {
        return      
      }
   
      # split up stuff
      regexp -nocase -- {^(.+?)@(.+?)\s(.+?)$} $input - link desc titem
      # fetch the html
      set ua "Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 OpenSSL/0.9.7e"
      set http [::http::config -useragent $ua -urlencoding "iso8859-1"]
      set url "http://www.google.com/translate_t?"
      set query [::http::formatQuery text $titem langpair "${link}\|${desc}" ]
        catch {set http [::http::geturl "$url" -query $query -timeout [expr 1000 * 10]]} error

      # CHECK CHECK
      upvar #0 $http state
      set incithcharset [string map -nocase {"UTF-" "utf-" "iso-" "iso" "windows-" "cp" "shift_jis" "shiftjis"} $state(charset)]
      if {$incith::google::debug > 0} {
        putserv "privmsg $incith::google::debugnick :\002url:\002 $url$query \002\037charset:\002\037 [string map -nocase {"iso-" "iso" "windows-" "cp" "shift_jis" "shiftjis"} $incithcharset]"
      }
        if {[string match -nocase "*couldn't open socket*" $error]} {
                return "Socket Error accessing '${url}' .. Does it exist?"
        }
        if { [::http::status $http] == "timeout" } {
                return "Connection has timed out"
        }
      set html [encoding convertto "utf-8" [::http::data $http]]
      ::http::cleanup $http

      regsub -all -nocase {<sup>(.+?)</sup>} $html {^\1} html
      regsub -all -nocase {<font.+?>} $html "" html
      regsub -all -nocase {</font>} $html "" html
      regsub -all -nocase {<span.*?>} $html "" html
      regsub -all -nocase {</span>} $html "" html
      regsub -all -nocase {<input.+?>} $html "" html
      regsub -all -nocase {(?:<i>|</i>)} $html "" html
      regsub -all "\t" $html " " html
      regsub -all "\n" $html " " html
      regsub -all "\r" $html " " html
      regsub -all "\v" $html " " html
      regsub -all "</li>" $html ". " html
      regsub -all ";;>" $html "" html

      # make sure everything is lowercase.
      set desc [string tolower $desc]
      set link [string tolower $link]
      regexp -- {<textarea name=utrans.+?id=suggestion>(.+?)</textarea>} $html {} match
        set match [incithencode [descdecode $match]]

      if {$match != ""} {
       return "Google says\: \(${link}\-\>${desc}\)\ ${match}"
      } else {
        return "Google error\: \(${link}\-\>${desc}\)\ This translation pair is not supported."
      }
      return $output
    }
'''

def load(bot):
        pass

def unload(bot):
        pass

def main(bot, user,target, msg):
        # Prints help
        if len(msg.split()) == 1:
                bot.message(user,target, __doc__)
                return None

        if msg.split()[1].upper() == 'HELP':
                bot.message(user, target, __doc__)
                return None

        if msg.split()[1].upper() == 'LIST':
                bot.message(user, target,  'Arabic: ar | Bulgarian: bg | Chinese: zh-CN | Chinese (Traditional): zh-TW | Croatian: hr | Czech: cs | Danish: da | Dutch: nl | English: en | Finnish: fi | French: fr | German: de | Greek: el | Hindi: hi | Italian: it | Japanese: ja | Korean: ko | Norwegian: no | Polish: pl | Portuguese: pt | Romanian: ro | Russian: ru | Spanish: es | Swedish: sv')
                return None

        if len(msg.split()) == 2:
                bot.message(user, target, __doc__)
                return None

        sep = re.compile(':|@')
        sep = sep.search(msg.split()[1])
        langs = msg.split()[1].split(sep.group())
        source_language = langs[0]
        to_language = langs[1]
        search_string = msg.split(' ', 2)[2]
        url_string = search_string.replace(' ','+')

        url='http://translate.google.com/translate_t?sl=' + source_language + '&tl=' + to_language + '&q=' + url_string
        html = webbot.bot(url)
       
        translation = re.search('id=result_box .+?>(?P<string>.+?)</div>',html).group('string')
        bot.message(user, target, user.split('!')[0] + ': ' + search_string + ' (' + source_language + '->' + to_language + ') ' + translation)

