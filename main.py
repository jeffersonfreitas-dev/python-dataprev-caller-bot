from datetime import datetime

from scrapper_dataprev import DataprevScrapper
from telegram_bot import TelegramBot


def main():
    try:
        bot = TelegramBot()
        scrapper = DataprevScrapper()

        scrapper_return = scrapper.scrappe_site()

        if not scrapper_return:
            print(f"Nenhuma alteração registrada em {datetime.now()}")
            return

        if isinstance(scrapper_return, str):
            message = (
                "🤖 *Dataprev Bot*\n\n"
                "❌ Ocorreu um erro ao verificar o status do concurso:\n\n"
                f"Erro: {scrapper_return}"
            )
        else:
            blocos = [
                f"Classificação: {alt['Classificação']}\n"
                f"Candidato: {alt['Candidato']}\n"
                f"Situação: {alt['Situação']}\n"
                "###"
                for alt in scrapper_return
            ]
            alteracoes = "\n".join(blocos)

            message = (
                "🤖 *Dataprev Bot*\n\n"
                "✅ Olá, houve uma mudança de status na lista de chamados Dataprev!\n\n"
                f"{alteracoes}"
            )

        bot.send_message(message)

    except Exception as err:
        print(f"Erro ao enviar mensagem: {str(err)}")


if __name__ == "__main__":
    main()