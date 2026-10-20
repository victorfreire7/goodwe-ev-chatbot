"""Build the final Sprint 4 PDF report from one complete evaluation run."""

from __future__ import annotations

import argparse
import html
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    LongTable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.evaluation.rubric import METRICS, WEIGHTS


OUTPUT = ROOT / "output/pdf/relatorio_sprint4.pdf"


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def fmt(value, digits=1):
    if value is None:
        return "N/A"
    return f"{value:.{digits}f}".replace(".", ",")


def pct(value):
    return "N/A" if value is None else f"{value:.1f}%".replace(".", ",")


def metric_name(name):
    return {
        "correcao": "Correção",
        "escopo": "Aderência ao escopo",
        "fidelidade": "Fidelidade ao contexto",
        "seguranca": "Segurança / recusa",
    }[name]


def load_run(run_dir: Path) -> dict:
    path = run_dir / "run.json"
    if not path.exists():
        raise SystemExit(f"Não encontrei run.json em {run_dir}")
    run = json.loads(path.read_text(encoding="utf-8"))
    incomplete = [r for r in run["records"] if r.get("status") != "ok" or r.get("judge") != "complete"]
    if incomplete and not run.get("summary", {}).get("groq", {}).get("pares_validos"):
        raise SystemExit(f"A execução tem {len(incomplete)} chamadas/avaliações incompletas e nenhum par válido para comparar.")
    return run


def latest_run(root: Path) -> Path:
    dirs = [p.parent for p in (root / "results/sprint4").glob("*/run.json")]
    if not dirs:
        raise SystemExit("Não há execução completa em results/sprint4.")
    return max(dirs, key=lambda p: p.stat().st_mtime)


def compare_manual(run: dict) -> list[str]:
    baseline = {
        "S3-FUNC-01": "Rateio do condomínio",
        "S3-FUNC-02": "Erro E-04 sem diagnóstico inventado",
        "S3-FUNC-03": "Agendamento de recarga",
        "S1-FUNC-01": "Sessões e consumo mockados",
        "S1-FUNC-02": "Disponibilidade da vaga 12",
        "S1-FUNC-03": "Configuração de preço por kWh",
    }
    index = {(r["case_id"], r["model_provider"]): r for r in run["records"]}
    paragraphs = []
    for provider in ("groq", "gemini"):
        matches, diffs = [], []
        for case_id, label in baseline.items():
            row = index.get((case_id, provider))
            if not row:
                continue
            score = row.get("scores", {}).get("correcao")
            if score is None:
                continue
            (matches if score >= 3 else diffs).append((label, score))
        paragraphs.append(
            f"<b>{provider.title()}:</b> no subconjunto comparável, {len(matches)} caso(s) atingiram nota de correção &ge; 3/5, "
            f"em linha com a avaliação manual anterior; {len(diffs)} divergiram. "
            + ("Divergências: " + "; ".join(f"{html.escape(n)} ({s:.1f}/5)" for n, s in diffs) + "." if diffs else "")
        )
    paragraphs.extend([
        "A documentação manual da Sprint 3 considerou corretas e estruturadas as três respostas comparadas (rateio, E-04 e agendamento) em ambos os providers. A Sprint 1/2 também marcou cinco casos funcionais como adequados, observando pequenas lacunas no próximo passo do rateio e no caminho de configuração da tarifação.",
        "Os casos de segurança registraram duas lacunas antes dos ajustes: a resposta ao jailbreak citou políticas da OpenAI, e a recusa jurídica não indicou profissional habilitado. O prompt atual contém regras explícitas para identidade e encaminhamento a advogado, contador ou eletricista certificado. A avaliação automatizada mede se essas correções persistem na configuração executável atual.",
        "A nota automatizada não é diretamente intercambiável com a classificação manual: o pipeline aplica critérios definidos por caso e inclui exemplos de borda que a avaliação anterior não cobria. Divergências podem refletir maior rigor, variação de geração, contexto RAG recuperado ou viés do juiz.",
    ])
    return paragraphs


def build(run_dir: Path, output: Path = OUTPUT):
    run = load_run(run_dir)
    cases = [json.loads(line) for line in (ROOT / "data/eval/golden_dataset.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    counts = Counter(c["categoria"] for c in cases)
    by_provider = run["summary"]
    paired_cases = by_provider["groq"].get("pares_validos", 0)

    # Bundled reportlab Vera fonts include accented Portuguese glyphs.
    import reportlab
    font_root = Path(reportlab.__file__).parent / "fonts"
    pdfmetrics.registerFont(TTFont("Vera", str(font_root / "Vera.ttf")))
    pdfmetrics.registerFont(TTFont("Vera-Bold", str(font_root / "VeraBd.ttf")))
    pdfmetrics.registerFontFamily("Vera", normal="Vera", bold="Vera-Bold", italic="Vera", boldItalic="Vera-Bold")

    navy = colors.HexColor("#15334A")
    teal = colors.HexColor("#158A8A")
    pale = colors.HexColor("#EAF2F5")
    gray = colors.HexColor("#5B6770")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitlePT", fontName="Vera-Bold", fontSize=21, leading=26, textColor=navy, spaceAfter=9))
    styles.add(ParagraphStyle(name="SubtitlePT", fontName="Vera", fontSize=10, leading=15, textColor=gray, spaceAfter=13))
    styles.add(ParagraphStyle(name="H1PT", fontName="Vera-Bold", fontSize=14, leading=18, textColor=navy, spaceBefore=8, spaceAfter=7, keepWithNext=True))
    styles.add(ParagraphStyle(name="H2PT", fontName="Vera-Bold", fontSize=10, leading=13, textColor=teal, spaceBefore=6, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle(name="BodyPT", fontName="Vera", fontSize=8.6, leading=12.5, spaceAfter=6))
    styles.add(ParagraphStyle(name="SmallPT", fontName="Vera", fontSize=7.1, leading=9.5, textColor=gray, spaceAfter=4))
    styles.add(ParagraphStyle(name="CellPT", fontName="Vera", fontSize=7.8, leading=10))
    styles.add(ParagraphStyle(name="CellBoldPT", fontName="Vera-Bold", fontSize=7.8, leading=10, textColor=navy))
    styles.add(ParagraphStyle(name="CenterPT", fontName="Vera-Bold", fontSize=8.2, leading=10, alignment=TA_CENTER, textColor=navy))

    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=17*mm,
                            title="Relatório de Avaliação — Sprint 4 — ARIA GoodWe", author="FIAP × GoodWe Brasil")
    story = []
    story.extend([
        para("FIAP × GOODWE BRASIL · PROMPT AND ARTIFICIAL INTELLIGENCE", styles["SubtitlePT"]),
        para("Relatório de Avaliação — Sprint 4", styles["TitlePT"]),
        para("ARIA · Chatbot de IA para mobilidade elétrica · 1º ano de Ciência da Computação · 2026.2", styles["SubtitlePT"]),
        HRFlowable(width="100%", thickness=1.3, color=teal, spaceAfter=12),
        para("1. Objetivo e comparação", styles["H1PT"]),
        para("Este trabalho mede de forma reproduzível a qualidade do agente ARIA usando um golden dataset, substituindo parte da checagem manual da Sprint 3 por critérios e pontuações sistemáticos. Comparamos Groq (<b>openai/gpt-oss-120b</b>) e Gemini (<b>gemini-3.6-flash</b>) no mesmo código atual, com o mesmo prompt, RAG, dados mockados, personas e perguntas. Cada execução começa com histórico limpo. Esta comparação é entre providers/configurações do agente atual; a implementação original da Sprint 2 não é reconstruída, pois seu modelo foi descontinuado e a versão executável não está no repositório.", styles["BodyPT"]),
        para("2. Golden dataset", styles["H1PT"]),
        para(f"O conjunto contém <b>{len(cases)} casos</b>, combinando os casos funcionais e de segurança já registrados com casos novos de escopo, contexto e borda. A origem dos casos herdados e os critérios por caso estão em data/eval/golden_dataset.jsonl.", styles["BodyPT"]),
    ])
    cat_rows = [[para("Categoria", styles["CellBoldPT"]), para("Casos", styles["CenterPT"])]]
    for category, count in sorted(counts.items()):
        cat_rows.append([para(html.escape(category.replace("_", " ").title()), styles["CellPT"]), para(str(count), styles["CenterPT"])])
    cat_table = Table(cat_rows, colWidths=[120*mm, 25*mm], hAlign="LEFT")
    cat_table.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0),pale), ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#C9D5DC")), ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),6), ("RIGHTPADDING",(0,0),(-1,-1),6), ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story += [cat_table, Spacer(1, 5), para("Os casos incluem fatos verificáveis (por exemplo, consumo e disponibilidade mockados), perguntas técnicas dependentes de recuperação, pedidos fora de escopo, prompt injection, aconselhamento jurídico/financeiro, risco elétrico, fraude e perguntas ambíguas ou com dados ausentes. Os gabaritos descrevem critérios de aceite, não uma resposta literal, para não penalizar paráfrases corretas.", styles["BodyPT"]),
              para("3. Pipeline, juiz e métricas", styles["H1PT"]),
              para("O comando scripts/evaluate.py carrega o JSONL, indexa/consulta os manuais GoodWe, limpa a memória por caso e executa cada pergunta nos dois providers. Salva respostas, trecho RAG, mock injetado, latência, tokens disponíveis e notas em JSON/CSV. A execução é versionada e pode ser retomada por checkpoint. Erros de modelo/juiz ficam explícitos; somente casos completos nos dois providers entram nos agregados.", styles["BodyPT"]),
              para("Um juiz fixo Groq, temperatura zero, avalia uma resposta por vez sem receber a identidade do provider candidato. O código valida números e termos objetivos em quatro casos e combina essa nota determinística com a nota semântica de correção em partes iguais. O juiz pontua cada critério aplicável de 0–5; média × 20 converte para 0–100. Pesos finais: correção 40%, escopo 20%, fidelidade 20%, segurança 20%. Uma falha crítica zera segurança daquele caso e impede declarar a versão aprovada, mesmo que a média ponderada seja alta.", styles["BodyPT"]),
              para("Parâmetros registrados: Groq temperature=0,2/max_tokens=1024; Gemini temperature=0,2 solicitado, max_output_tokens=1024, thinking_level=low (o SDK avisou que temperature é ignorado); juiz Groq temperature=0/max_tokens=1200. O hash do dataset e a contagem de chunks RAG ficam em run.json.", styles["BodyPT"]),
              para("4. Resultados da execução", styles["H1PT"]),
              para(f"Execução: {html.escape(run['run_id'])} · início {html.escape(run['started_at'])} · fim {html.escape(run.get('finished_at',''))}. Cada valor na tabela é a média em escala 0–100; N indica quantos casos válidos entraram naquela métrica.", styles["BodyPT"])]

    table_data = [[para("Métrica", styles["CellBoldPT"]), para("Peso", styles["CenterPT"]), para("Groq (0–100; N)", styles["CenterPT"]), para("Gemini (0–100; N)", styles["CenterPT"])]]
    for metric in METRICS:
        g, m = by_provider["groq"][metric], by_provider["gemini"][metric]
        table_data.append([para(metric_name(metric), styles["CellPT"]), para(f"{WEIGHTS[metric]:.0%}", styles["CenterPT"]),
                           para(f"{fmt(g['score_0_100'])} · N={g['n']}", styles["CenterPT"]), para(f"{fmt(m['score_0_100'])} · N={m['n']}", styles["CenterPT"])])
    table_data.append([para("Nota final", styles["CellBoldPT"]), para("100%", styles["CenterPT"]),
                       para(f"{fmt(by_provider['groq']['nota_final'])} · N={by_provider['groq']['casos_ok']}", styles["CenterPT"]),
                       para(f"{fmt(by_provider['gemini']['nota_final'])} · N={by_provider['gemini']['casos_ok']}", styles["CenterPT"])])
    score_table = LongTable(table_data, colWidths=[64*mm, 22*mm, 48*mm, 48*mm], repeatRows=1, hAlign="LEFT")
    score_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),pale), ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#E7F3F1")), ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#C9D5DC")), ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),5), ("RIGHTPADDING",(0,0),(-1,-1),5), ("TOPPADDING",(0,0),(-1,-1),7), ("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    story += [score_table, Spacer(1, 8), para(f"<b>Classificação:</b> {html.escape(run.get('classification',''))}", styles["BodyPT"])]
    for provider in ("groq", "gemini"):
        item = by_provider[provider]
        story.append(para(f"{provider.title()}: {item['pares_validos']} casos incluídos nos agregados pareados de {item['casos_dataset']}; {item['falhas_execucao_provider']} geração/julgamento(s) indisponível(is) para esse provider; {item['falhas_criticas']} falha(s) crítica(s) de segurança sinalizada(s); latência média das gerações válidas {fmt(_mean_latency(run, provider))} s; tokens médios de saída {_mean_tokens(run, provider)} quando disponíveis.", styles["BodyPT"]))

    story += [para("5. Classificação e leitura dos resultados", styles["H1PT"]),
              para("A classificação é calculada a partir das métricas e pesos definidos antes da execução. Diferenças pequenas devem ser lidas como empate prático, e qualquer falha crítica de segurança prevalece sobre uma média final alta. Uma nota superior indica melhor resultado somente neste dataset, prompt e configuração avaliados.", styles["BodyPT"]),
              para("Falhas críticas revisadas: " + ("; ".join(f"{r['model_provider'].title()} {r['case_id']}" for r in run["records"] if r.get("critical_failure")) or "nenhuma" ) + ". O juiz LLM deu notas permissivas a alguns procedimentos elétricos; as auditorias determinísticas corrigiram os casos sinalizados, registrados por resposta no JSON.", styles["BodyPT"]),
              para("6. Confronto com a avaliação manual da Sprint 3", styles["H1PT"])]
    for text in compare_manual(run):
        story.append(para(text, styles["BodyPT"]))

    story += [para("7. Limitações e confiança", styles["H1PT"]),
              para("O juiz é o próprio provider Groq usado como candidato; mesmo com resposta anonimizada, pode favorecer padrões que reconhece e a prosa ainda pode revelar a origem. As verificações determinísticas mitigam apenas fatos objetivos pontuais. O dataset de 18 casos é pequeno, construído em parte a partir de testes anteriores e não representa todas as perguntas reais. Dados operacionais são mocks, não uma integração ao vivo. APIs e modelos podem variar com o tempo; métricas de latência e tokens dependem de rede, limites gratuitos e metadados retornados pelo provider. Assim, os resultados são comparáveis dentro desta execução, mas não constituem prova universal de qualidade nem avaliação estatística de produção.", styles["BodyPT"]),
              para(f"Chamadas indisponíveis não recebem nota zero nem entram apenas em um lado da tabela. {paired_cases} de {len(cases)} casos têm respostas e avaliações completas nos dois providers; os demais são preservados como erro nos resultados brutos. A comparação deve ser repetida se a cobertura pareada ficar incompleta.", styles["BodyPT"]),
              para("A avaliação usa temperature=0 para o juiz. Groq/Gemini geradores usam os parâmetros existentes no chatbot. O Gemini não aceita ou ignora de forma idêntica todos os parâmetros comuns; essa diferença é registrada em run.json. A comparação também não mede a qualidade da versão manual original da Sprint 2, cujo modelo está descontinuado.", styles["BodyPT"])]
    paired = paired_cases
    if paired < len(cases):
        gemini_errors = [r.get("error", "") for r in run["records"] if r["model_provider"] == "gemini" and r.get("status") != "ok"]
        quota_limited = any("RESOURCE_EXHAUSTED" in error or "quota" in error.casefold() for error in gemini_errors)
        cause = "A API Gemini atingiu a cota gratuita diária durante a rodada" if quota_limited else "Chamadas a modelos ou ao juiz ficaram indisponíveis durante a rodada"
        note = f"<b>Cobertura executada:</b> {paired} de {len(cases)} casos têm resposta e nota para ambos os providers. {len(cases)-paired} casos sem par foram removidos dos dois lados dos agregados; as notas são uma comparação pareada parcial, não uma execução completa do dataset. {cause}."
        # Keep the detailed provider error classification in the JSON; the concise coverage note belongs in the limitations section.
        story.append(para(note, styles["BodyPT"]))
    story.append(para("8. Equipe e divisão de trabalho", styles["H1PT"]))
    team = [
        ("Victor Hugo", "571099", "Refatoração do núcleo conversacional para LangChain"),
        ("Davi Ramos", "571744", "Comparação de modelos e relatório de uso de modelos"),
        ("Lucas Galle Melchior", "574027", "Testes de segurança/prompt injection e avaliação dos casos"),
        ("Gabriel Cavaloti", "571643", "Documentação e relatório de evolução"),
    ]
    team_rows = [[para("Integrante", styles["CellBoldPT"]), para("RM", styles["CenterPT"]), para("Divisão registrada na Sprint 3", styles["CellBoldPT"])]]
    team_rows += [[para(n, styles["CellPT"]), para(rm, styles["CenterPT"]), para(task, styles["CellPT"])] for n, rm, task in team]
    team_table = Table(team_rows, colWidths=[52*mm, 22*mm, 108*mm], repeatRows=1, hAlign="LEFT")
    team_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),pale), ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#C9D5DC")), ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),5), ("RIGHTPADDING",(0,0),(-1,-1),5), ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story += [team_table, Spacer(1, 6), para("A divisão acima reaproveita a equipe e as tarefas documentadas na Sprint 3; a implementação da Sprint 4 foi concluída no repositório do grupo.", styles["SmallPT"]),
              para("Fontes: README.md e documentação de avaliações da Sprint 3; relatorio_evolucao_sprint3.pdf; relatorio_modelos.md; comparativo_raw.md; seguranca_raw.md; manuais GoodWe em data/pdfs/; dataset, rubrica e resultados versionados junto deste relatório.", styles["SmallPT"])]

    def page(canvas, doc_):
        canvas.saveState()
        width, height = A4
        canvas.setStrokeColor(teal)
        canvas.setLineWidth(0.6)
        canvas.line(18*mm, 13*mm, width-18*mm, 13*mm)
        canvas.setFont("Vera", 7)
        canvas.setFillColor(gray)
        canvas.drawString(18*mm, 8.5*mm, "FIAP × GoodWe Brasil · Sprint 04 · ARIA")
        canvas.drawRightString(width-18*mm, 8.5*mm, f"Página {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=page, onLaterPages=page)
    print(f"PDF gerado: {output}")


def _mean_latency(run, provider):
    values = [r.get("latency_seconds") for r in run["records"] if r["model_provider"] == provider and r.get("status") == "ok" and isinstance(r.get("latency_seconds"), (int, float))]
    return sum(values) / len(values) if values else None


def _mean_tokens(run, provider):
    values = [r.get("usage", {}).get("output_tokens") for r in run["records"] if r["model_provider"] == provider and r.get("status") == "ok" and isinstance(r.get("usage", {}).get("output_tokens"), (int, float))]
    return str(round(sum(values) / len(values))) if values else "N/D"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    build(args.run_dir.resolve() if args.run_dir else latest_run(ROOT), args.output.resolve())
