import os, math
from datetime import timedelta
from django.conf import settings
from django.db.models import Q as Cond, Max, Count
from django.utils import timezone
from gtts import gTTS
from mutagen.mp3 import MP3

from log.models import Log
from pendencies.models import Pendencies

audio_url = os.path.join(settings.MEDIA_URL, "avatar_audio")
audiodir = os.path.join(settings.MEDIA_ROOT, "avatar_audio")


def genAudioFile(speech, subtitle, filename, emotion=""):
    if not os.path.isdir(audiodir):
        os.makedirs(audiodir)

    filepath = os.path.join(audiodir, filename)
    fileurl = os.path.join(audio_url, filename)

    tts = gTTS(text=speech, lang="pt-br")
    tts.save(filepath)

    track = MP3(filepath)

    return {
        "file": fileurl,
        "duration": track.info.length,
        "text": subtitle,
        "emotion": emotion,
    }


def generalInfo(subject, user):
    audios = []

    tts = "Olá, %s!" % (str(user))
    ttr = "Olá, <b>%s</b>!" % (str(user))
    filename = "welcome_%s.mp3" % (str(user))
    audios.append(genAudioFile(tts, ttr, filename))

    logs = Log.objects.filter(
        datetime__date__gte=subject.init_date,
        component="subject",
        action="view",
        resource="analytics",
        user_id=user.id,
        context__contains={"subject_id": subject.id},
    )

    if not logs.exists():
        tts = "Seja bem-vindo ao painel de estudante"
        ttr = "Seja bem-vindo ao painel de estudante"
        filename = "intro.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

        tts = "O painel de analytics serve para te manter atento em relação às atividades e recursos da disciplina"
        ttr = "O painel de analytics serve para te manter atento em relação às atividades e recursos da disciplina"
        filename = "definition.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

        tts = "Acesse-o regularmente"
        ttr = "Acesse-o regularmente"
        filename = "warning.mp3"
        audios.append(genAudioFile(tts, ttr, filename))
    else:
        off_days = (timezone.now() - logs.last().datetime).days
        if off_days > 0:
            if off_days > 1:
                tts = "Seu último acesso foi há %s dias" % (str(off_days))
                ttr = "Seu último acesso foi há <b>%s dias</b>" % (str(off_days))
            else:
                tts = "Seu último acesso foi ontem"
                ttr = "Seu último acesso foi <b>ontem</b>"
            filename = "days_off.mp3"
            audios.append(genAudioFile(tts, ttr, filename, "crying"))
    return audios


def cloudInfo(tagData):
    audios = []

    data = sorted(tagData, key=lambda x: x["qtd_access"], reverse=True)
    data = data[0 : math.floor(30 / 1000 * 775)]

    tts = "Esta é a nuvem de tags"
    ttr = "Esta é a <b>nuvem de tags</b>"
    filename = "cloud1.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    tts = "Através dela é possível identificar as tags mais populares da disciplina"
    ttr = (
        "Através dela é possível identificar as <b>tags<b> mais populares da disciplina"
    )
    filename = "cloud2.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    tts = "Quanto maior a palavra, mais a classe acessou"
    ttr = "Quanto <b>maior</b> a palavra, <b>mais</b> a classe acessou"
    filename = "cloud3.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    tts = "Quanto mais clara, mais vezes você acessou"
    ttr = "Quanto <b>mais clara</b>, <b>mais vezes</b> você acessou"
    filename = "cloud4.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    if data:
        most_accessed = data[0]

        tts = "Note que a tag %s tem mais acesso da classe" % (
            most_accessed["tag_name"]
        )
        ttr = "Note que a tag <b>%s</b> tem mais acesso da classe" % (
            most_accessed["tag_name"]
        )
        filename = "cloud5.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

        data_my = sorted(data, key=lambda x: x["qtd_my_access"], reverse=True)
        most_accessed = data_my[0]

        tts = "e a tag %s foi mais acessada por você" % (most_accessed["tag_name"])
        ttr = "e a tag <b>%s</b> foi mais acessada por você" % (
            most_accessed["tag_name"]
        )
        filename = "cloud6.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

        tts = "Para ver os recursos de uma tag basta clicar nela"
        ttr = "Para ver os recursos de uma tag basta clicar nela"
        filename = "cloud7.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

    return audios


def cloudTips(tagData):
    audios = []

    data = sorted(tagData, key=lambda x: x["qtd_access"], reverse=True)
    data = data[0 : math.floor(30 / 1000 * 775)]

    if data:
        most_accessed = data[0]

        if most_accessed["qtd_my_access"] > 0:
            tts = "Há tags em alta que estão sendo vistas por toda a turma"
            ttr = "Há tags em alta que estão sendo vistas por toda a turma"
            filename = "most_accessed.mp3"
            audios.append(genAudioFile(tts, ttr, filename, "surprise"))

            tts = (
                "É importante que você também acesse recursos dessas tags, por exemplo, %s."
                % (most_accessed["tag_name"])
            )
            ttr = (
                "É importante que você também acesse recursos dessas tags, por exemplo, <b class='shineTag'>%s</b>."
                % (most_accessed["tag_name"])
            )
            filename = "most_accessed2.mp3"
            audios.append(genAudioFile(tts, ttr, filename))

            return audios

        not_accessed = [d for d in data if d["qtd_my_access"] == 0]

        if len(not_accessed) > 0:
            tts = "Não pule ou esqueça de acessar todos os recursos disponíveis"
            ttr = "Não pule ou esqueça de acessar todos os recursos disponíveis"
            filename = "less_accessed.mp3"
            audios.append(genAudioFile(tts, ttr, filename))

            if len(not_accessed) == 1:
                tts = (
                    "Você deixou de ver recursos de tags importantes, por exemplo, %s"
                    % (not_accessed[0]["tag_name"])
                )
                ttr = (
                    "Você deixou de ver recursos de tags importantes, por exemplo, <b class='shineTag'>%s</b>"
                    % (not_accessed[0]["tag_name"])
                )
                filename = "less_accessed2.mp3"
                audios.append(genAudioFile(tts, ttr, filename, "sad"))

            elif len(not_accessed) == 2:
                tts = (
                    "Você deixou de ver recursos de tags importantes, por exemplo, %s e %s"
                    % (not_accessed[0]["tag_name"], not_accessed[1]["tag_name"])
                )
                ttr = (
                    "Você deixou de ver recursos de tags importantes, por exemplo, <b class='shineTag'>%s</b> e <b class='shineTag'>%s</b>"
                    % (not_accessed[0]["tag_name"], not_accessed[1]["tag_name"])
                )
                filename = "less_accessed2.mp3"
                audios.append(genAudioFile(tts, ttr, filename, "sad"))

            elif len(not_accessed) >= 3:
                tts = (
                    "Você deixou de ver recursos de tags importantes, por exemplo, %s, %s e %s"
                    % (
                        not_accessed[0]["tag_name"],
                        not_accessed[1]["tag_name"],
                        not_accessed[2]["tag_name"],
                    )
                )
                ttr = (
                    "Você deixou de ver recursos de tags importantes, por exemplo, <b class='shineTag'>%s</b>, <b class='shineTag'>%s</b> e <b class='shineTag'>%s</b>"
                    % (
                        not_accessed[0]["tag_name"],
                        not_accessed[1]["tag_name"],
                        not_accessed[2]["tag_name"],
                    )
                )
                filename = "less_accessed2.mp3"
                audios.append(genAudioFile(tts, ttr, filename, "sad"))

            return audios

        tts = "Parabéns! Continue acessando regularmente o ambiente da disciplina"
        ttr = "Parabéns! Continue acessando regularmente o ambiente da disciplina"
        filename = "congratulations.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

        tts = "Você pode revisar e fazer exercícios, bons estudos!"
        ttr = "Você pode revisar e fazer exercícios, bons estudos!"
        filename = "congratulations2.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

    return audios


def indicatorsInfo():
    audios = []

    tts = "Este é o gráfico de indicadores"
    ttr = "Este é o <b>gráfico de indicadores</b>"
    filename = "indicators1.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    tts = "Através dele é possível acompanhar e comparar o desempenho da turma e o seu"
    ttr = "Através dele é possível acompanhar e comparar o desempenho da turma e o seu"
    filename = "indicators2.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    tts = (
        "Acesse constantemente o ambiente da disciplina para melhorar seus indicadores"
    )
    ttr = (
        "Acesse constantemente o ambiente da disciplina para melhorar seus indicadores"
    )
    filename = "indicators3.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    return audios


def indicatorsTips(subject, indicatorsData):
    audios = []

    subjectAccess = indicatorsData[0]
    subjectAccessDays = indicatorsData[1]
    resourcesAccess = indicatorsData[2]
    resourcesDistinctAccess = indicatorsData[3]
    tasksRealized = indicatorsData[4]

    pendCount = Pendencies.objects.filter(
        resource__topic__subject=subject.id,
        resource__visible=True,
        begin_date__date__lt=timezone.now(),
        end_date__date__gte=timezone.now() - timedelta(days=6),
    ).count()
    top = True
    if (
        subjectAccess["my_access"] < subjectAccess["percentil_4"]
        or subjectAccess["my_access"] <= 0
    ):
        filename = "indicators6.mp3"
        if subjectAccess["my_access"] == 0:
            tts = "Você não acessou nenhuma vez o ambiente durante a semana"
            ttr = "Você não acessou <b>nenhuma</b> vez o ambiente durante a semana"
            audios.append(genAudioFile(tts, ttr, filename, "crying"))
        elif subjectAccess["my_access"] == 1:
            if subjectAccessDays["my_access"] == 1:
                tts = "Você acessou %s vez o ambiente, em %s dia diferente" % (
                    str(subjectAccess["my_access"]),
                    str(subjectAccessDays["my_access"]),
                )
                ttr = (
                    "Você acessou <b>%s</b> vez o ambiente, em <b>%s</b> dia diferente"
                    % (
                        str(subjectAccess["my_access"]),
                        str(subjectAccessDays["my_access"]),
                    )
                )
                audios.append(genAudioFile(tts, ttr, filename))
            else:
                tts = "Você acessou %s vez o ambiente, em %s dias diferentes" % (
                    str(subjectAccess["my_access"]),
                    str(subjectAccessDays["my_access"]),
                )
                ttr = (
                    "Você acessou <b>%s</b> vez o ambiente, em <b>%s</b> dias diferentes"
                    % (
                        str(subjectAccess["my_access"]),
                        str(subjectAccessDays["my_access"]),
                    )
                )
                audios.append(genAudioFile(tts, ttr, filename))
        else:
            tts = "Você acessou %s vezes o ambiente, em %s dias diferentes" % (
                str(subjectAccess["my_access"]),
                str(subjectAccessDays["my_access"]),
            )
            ttr = (
                "Você acessou <b>%s</b> vezes o ambiente, em <b>%s</b> dias diferentes"
                % (str(subjectAccess["my_access"]), str(subjectAccessDays["my_access"]))
            )
            audios.append(genAudioFile(tts, ttr, filename))

        tts = "Acesse o ambiente da disciplina constantemente"
        ttr = "Acesse o ambiente da disciplina constantemente"
        filename = "indicators4.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

        tts = "Planeje sua rotina"
        ttr = "<b>Planeje sua rotina</b>"
        filename = "indicators5.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

        return audios

    if (
        resourcesAccess["my_access"] < resourcesAccess["percentil_4"]
        or resourcesAccess["my_access"] <= 0
    ):
        filename = "indicators11.mp3"

        if resourcesAccess["my_access"] == 0:
            tts = "Você não acessou nenhuma vez os recursos da disciplina"
            ttr = "Você não acessou <b>nenhuma</b> vez os recursos da disciplina"
            audios.append(genAudioFile(tts, ttr, filename, "crying"))
        elif resourcesAccess["my_access"] == 1:
            if resourcesDistinctAccess["my_access"] == 1:
                tts = (
                    "Você acessou %s vez os recursos da disciplina, sendo %s recurso diferente"
                    % (
                        str(resourcesAccess["my_access"]),
                        str(resourcesDistinctAccess["my_access"]),
                    )
                )
                ttr = (
                    "Você acessou <b>%s</b> vez os recursos da disciplina, sendo <b>%s</b> recurso diferente"
                    % (
                        str(resourcesAccess["my_access"]),
                        str(resourcesDistinctAccess["my_access"]),
                    )
                )
                audios.append(genAudioFile(tts, ttr, filename, "crying"))
            else:
                tts = (
                    "Você acessou %s vez os recursos da disciplina, sendo %s recursos diferentes"
                    % (
                        str(resourcesAccess["my_access"]),
                        str(resourcesDistinctAccess["my_access"]),
                    )
                )
                ttr = (
                    "Você acessou <b>%s</b> vez os recursos da disciplina, sendo <b>%s</b> recursos diferentes"
                    % (
                        str(resourcesAccess["my_access"]),
                        str(resourcesDistinctAccess["my_access"]),
                    )
                )
                audios.append(genAudioFile(tts, ttr, filename, "crying"))
        else:
            tts = (
                "Você acessou %s vezes os recursos da disciplina, sendo %s recursos distintos"
                % (
                    str(resourcesAccess["my_access"]),
                    str(resourcesDistinctAccess["my_access"]),
                )
            )
            ttr = (
                "Você acessou <b>%s</b> vezes os recursos da disciplina, sendo <b>%s</b> recursos distintos"
                % (
                    str(resourcesAccess["my_access"]),
                    str(resourcesDistinctAccess["my_access"]),
                )
            )
            audios.append(genAudioFile(tts, ttr, filename))

        tts = "Não pule ou deixe de acessar os recursos"
        ttr = "Não pule ou deixe de acessar os recursos"
        filename = "indicators12.mp3"
        audios.append(genAudioFile(tts, ttr, filename, "sad"))

        # return audios
        top = False

    if (
        tasksRealized["my_access"] < tasksRealized["percentil_4"]
        or tasksRealized["my_access"] <= 0
    ):
        filename = "indicators7.mp3"
        if tasksRealized["my_access"] == 0:
            tts = "Você não realizou nenhuma das tarefas pontualmente"
            ttr = "Você não realizou <b>nenhuma</b> das tarefas pontualmente"
            audios.append(genAudioFile(tts, ttr, filename, "sad"))
        else:
            tts = "Você realizou pontualmente apenas %s das %s tarefas" % (
                str(tasksRealized["my_access"]),
                str(pendCount),
            )
            ttr = "Você realizou pontualmente apenas <b>%s</b> das %s tarefas" % (
                str(tasksRealized["my_access"]),
                str(pendCount),
            )
            audios.append(genAudioFile(tts, ttr, filename))

        tts = (
            "As tarefas são fundamentais para complementar e consolidar a aprendizagem"
        )
        ttr = (
            "As tarefas são fundamentais para complementar e consolidar a aprendizagem"
        )
        filename = "indicators8.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

        tts = "Organize-se e mantenha o foco"
        ttr = "<b>Organize-se</b> e <b>mantenha o foco</b>"
        filename = "indicators9.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

        # return audios
        top = False
    if top is True:
        tts = "Parabéns! Continue acessando regularmente o ambiente da disciplina"
        ttr = "Parabéns! Continue acessando regularmente o ambiente da disciplina"
        filename = "indicators8.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

    return audios


def ganntInfo():
    audios = []

    tts = "Este é o gráfico de Gannt"
    ttr = "Este é o <b>gráfico de Gannt</b>"
    filename = "gannt1.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    tts = "Através dele é possível acompanhar e avaliar os prazos de tarefas da disciplina"
    ttr = "Através dele é possível acompanhar e avaliar os prazos de tarefas da disciplina"
    filename = "gannt2.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    tts = "Também podemos observar o percentual da turma que já realizou a tarefa"
    ttr = "Também podemos observar o percentual da turma que já realizou a tarefa"
    filename = "gannt3.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    tts = "Evite atrasos e organize-se, não deixe para depois!"
    ttr = "<b>Evite atrasos</b> e <b>organize-se</b>, não deixe para depois!"
    filename = "gannt4.mp3"
    audios.append(genAudioFile(tts, ttr, filename))

    return audios


def ganntTips(ganntData):
    audios = []

    today = timezone.now()

    finishedTasks = [
        t
        for t in ganntData
        if t["date"]["delay"] != "infinity" and t["date"]["delayDate"] < today
    ]
    finishedTasks = sorted(
        finishedTasks, key=lambda x: x["date"]["delayDate"], reverse=True
    )

    lostTasks = [t for t in finishedTasks if t["done"] == False]
    top = True
    if len(lostTasks) > 0:
        filename = "gannt5.mp3"
        if len(lostTasks) == 1:
            tts = (
                "Cuidado! Você deixou de realizar %s tarefa das %s tarefas finalizadas até o momento, como '%s'"
                % (
                    str(len(lostTasks)),
                    str(len(finishedTasks)),
                    lostTasks[0]["action"] + " " + lostTasks[0]["name"],
                )
            )
            ttr = (
                "Cuidado! Você deixou de realizar <b>%s</b> tarefa das <b>%s</b> tarefas finalizadas até o momento, como '<b>%s</b>'"
                % (
                    str(len(lostTasks)),
                    str(len(finishedTasks)),
                    lostTasks[0]["action"] + " " + lostTasks[0]["name"],
                )
            )
            audios.append(genAudioFile(tts, ttr, filename, "sad"))
        else:
            tts = (
                "Cuidado! Você deixou de realizar %s tarefas das %s tarefas finalizadas até o momento, como '%s'"
                % (
                    str(len(lostTasks)),
                    str(len(finishedTasks)),
                    lostTasks[0]["action"] + " " + lostTasks[0]["name"],
                )
            )
            ttr = (
                "Cuidado! Você deixou de realizar <b>%s</b> tarefas das <b>%s</b> tarefas finalizadas até o momento, como '<b>%s</b>'"
                % (
                    str(len(lostTasks)),
                    str(len(finishedTasks)),
                    lostTasks[0]["action"] + " " + lostTasks[0]["name"],
                )
            )
            audios.append(genAudioFile(tts, ttr, filename, "crying"))

        # return audios
        top = False

    initializedTasks = [
        t
        for t in ganntData
        if t["date"]["startDate"] <= today and t["date"]["endDate"] > today
    ]
    initializedTasks = sorted(initializedTasks, key=lambda x: x["date"]["endDate"])

    unstartedTasks = [t for t in initializedTasks if t["done"] == False]

    if len(unstartedTasks) > 0:
        tts = "Se liga! Algumas atividades estão próximas do fim, por exemplo, %s" % (
            unstartedTasks[0]["action"] + " " + unstartedTasks[0]["name"]
        )
        ttr = (
            "Se liga! Algumas atividades estão próximas do fim, por exemplo, <b>%s</b>"
            % (unstartedTasks[0]["action"] + " " + unstartedTasks[0]["name"])
        )
        filename = "gannt6.mp3"
        audios.append(genAudioFile(tts, ttr, filename, "surprise"))

        # return audios
        top = False

    nextTasks = [t for t in ganntData if t["date"]["startDate"] > today]
    nextTasks = sorted(nextTasks, key=lambda x: x["date"]["startDate"])

    if len(nextTasks) > 0:
        tts = (
            "Fique ligado! Nos próximos dias novas tarefas irão iniciar, como, '%s'"
            % (nextTasks[0]["action"] + " " + nextTasks[0]["name"])
        )
        ttr = (
            "Fique ligado! Nos próximos dias novas tarefas irão iniciar, como, '<b>%s</b>'"
            % (nextTasks[0]["action"] + " " + nextTasks[0]["name"])
        )
        filename = "gannt7.mp3"
        audios.append(genAudioFile(tts, ttr, filename, "suprise"))

        tts = "Organize-se e prepare-se para elas"
        ttr = "<b>Organize-se</b> e <b>prepare-se</b> para elas"
        filename = "gannt8.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

        # return audios
        top = False
    if top is True:
        tts = "Parabéns, continue acessando regularmente o ambiente da disciplina"
        ttr = "Parabéns, continue acessando regularmente o ambiente da disciplina"
        filename = "gannt9.mp3"
        audios.append(genAudioFile(tts, ttr, filename))

    return audios

