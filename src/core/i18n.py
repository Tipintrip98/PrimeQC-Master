"""
PrimeQC Master - Internationalization (i18n) Engine.
Provides instant multi-language switching across Italian, English, Spanish,
French, German, Portuguese, Japanese, and Simplified Chinese.
"""

import os
import json
from typing import Dict, Any, Callable, List

# Supported Language Definitions
LANGUAGES = {
    "it": {"name": "Italiano", "flag": "🇮🇹", "code": "it"},
    "en": {"name": "English", "flag": "🇬🇧", "code": "en"},
    "es": {"name": "Español", "flag": "🇪🇸", "code": "es"},
    "fr": {"name": "Français", "flag": "🇫🇷", "code": "fr"},
    "de": {"name": "Deutsch", "flag": "🇩🇪", "code": "de"},
    "pt": {"name": "Português", "flag": "🇵🇹", "code": "pt"},
    "ja": {"name": "日本語", "flag": "🇯🇵", "code": "ja"},
    "zh": {"name": "中文 (简体)", "flag": "🇨🇳", "code": "zh"},
}

# Translation Dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Main Window & Navigation
    "app_title": {
        "it": "PrimeQC Master - Suite Quality Control Amazon Prime Video",
        "en": "PrimeQC Master - Amazon Prime Video Quality Control Suite",
        "es": "PrimeQC Master - Suite de Control de Calidad Amazon Prime Video",
        "fr": "PrimeQC Master - Suite de Contrôle Qualité Amazon Prime Video",
        "de": "PrimeQC Master - Amazon Prime Video Qualitätskontroll-Suite",
        "pt": "PrimeQC Master - Suíte de Controle de Qualidade Amazon Prime Video",
        "ja": "PrimeQC Master - Amazon Prime Video 品質管理スイート",
        "zh": "PrimeQC Master - 亚马逊 Prime Video 质量控制套件"
    },
    "menu_file": {
        "it": "&File", "en": "&File", "es": "&Archivo", "fr": "&Fichier", "de": "&Datei", "pt": "&Arquivo", "ja": "ファイル(&F)", "zh": "文件(&F)"
    },
    "menu_open": {
        "it": "📂 Apri Master Video...", "en": "📂 Open Video Master...", "es": "📂 Abrir Master de Video...",
        "fr": "📂 Ouvrir Master Vidéo...", "de": "📂 Video-Master öffnen...", "pt": "📂 Abrir Master de Vídeo...",
        "ja": "📂 ビデオマスターを開く...", "zh": "📂 打开视频母版..."
    },
    "menu_subtitles": {
        "it": "🔤 Carica Sottotitoli Sidecar...", "en": "🔤 Load Sidecar Subtitles...", "es": "🔤 Cargar Subtítulos Sidecar...",
        "fr": "🔤 Charger Sous-titres Sidecar...", "de": "🔤 Sidecar-Untertitel laden...", "pt": "🔤 Carregar Legendas Sidecar...",
        "ja": "🔤 サイドカー字幕を読み込む...", "zh": "🔤 加载外挂字幕..."
    },
    "menu_save": {
        "it": "💾 Salva / Esporta Report QC...", "en": "💾 Save / Export QC Report...", "es": "💾 Guardar / Exportar Reporte QC...",
        "fr": "💾 Enregistrer / Exporter Rapport QC...", "de": "💾 QC-Bericht speichern / exportieren...", "pt": "💾 Salvar / Exportar Relatório QC...",
        "ja": "💾 QCレポートを保存/エクスポート...", "zh": "💾 保存/导出质检报告..."
    },
    "menu_reset": {
        "it": "🔄 Nuovo Controllo / Resetta", "en": "🔄 New Inspection / Reset", "es": "🔄 Nueva Inspección / Restablecer",
        "fr": "🔄 Nouvelle Inspection / Réinitialiser", "de": "🔄 Neue Prüfung / Zurücksetzen", "pt": "🔄 Nova Inspeção / Redefinir",
        "ja": "🔄 新規検査 / リセット", "zh": "🔄 新建检查 / 重置"
    },
    "menu_exit": {
        "it": "🚪 Esci", "en": "🚪 Exit", "es": "🚪 Salir", "fr": "🚪 Quitter", "de": "🚪 Beenden", "pt": "🚪 Sair", "ja": "🚪 終了", "zh": "🚪 退出"
    },
    "menu_profiles": {
        "it": "&Profili Amazon", "en": "&Amazon Profiles", "es": "&Perfiles Amazon", "fr": "&Profils Amazon", "de": "&Amazon-Profile", "pt": "&Perfis Amazon", "ja": "Amazonプロファイル(&P)", "zh": "亚马逊配置(&P)"
    },
    "menu_profile_settings": {
        "it": "⚙️ Gestione Standard & Tolleranze...", "en": "⚙️ Manage Standards & Tolerances...", "es": "⚙️ Gestionar Estándares y Tolerancias...",
        "fr": "⚙️ Gérer Standards et Tolérances...", "de": "⚙️ Standards & Toleranzen verwalten...", "pt": "⚙️ Gerenciar Padrões e Tolerâncias...",
        "ja": "⚙️ 規格と許容値の管理...", "zh": "⚙️ 管理标准与容差..."
    },
    "menu_utilities": {
        "it": "&Utility", "en": "&Utilities", "es": "&Utilidades", "fr": "&Utilitaires", "de": "&Dienstprogramme", "pt": "&Utilitários", "ja": "ユーティリティ(&U)", "zh": "实用工具(&U)"
    },
    "util_loudness": {
        "it": "🎚️ Correttore Automatico Loudness (-24 LKFS / -2 dBTP)", "en": "🎚️ Auto Loudness Conformer (-24 LKFS / -2 dBTP)",
        "es": "🎚️ Corrector Automático de Loudness (-24 LKFS / -2 dBTP)", "fr": "🎚️ Conformateur Auto Loudness (-24 LKFS / -2 dBTP)",
        "de": "🎚️ Auto-Loudness-Korrektur (-24 LKFS / -2 dBTP)", "pt": "🎚️ Corretor Automático de Loudness (-24 LKFS / -2 dBTP)",
        "ja": "🎚️ 自動ラウドネス補正 (-24 LKFS / -2 dBTP)", "zh": "🎚️ 自动响度合规化 (-24 LKFS / -2 dBTP)"
    },
    "util_prores": {
        "it": "🎞️ Transcoder Master ProRes 422 HQ & Deinterlacciatore", "en": "🎞️ ProRes 422 HQ Master Transcoder & Deinterlacer",
        "es": "🎞️ Transcodificador ProRes 422 HQ y Desentrelazador", "fr": "🎞️ Transcodeur ProRes 422 HQ et Désentrelaceur",
        "de": "🎞️ ProRes 422 HQ Master-Transcoder & Deinterlacer", "pt": "🎞️ Transcodificador ProRes 422 HQ e Desentrelaçador",
        "ja": "🎞️ ProRes 422 HQ マスタートランスコーダー & インターレース解除", "zh": "🎞️ ProRes 422 HQ 母版转码与反交错"
    },
    "util_calc": {
        "it": "📏 Calcolatore Spazio & Bitrate per Amazon", "en": "📏 Amazon Bitrate & Storage Calculator",
        "es": "📏 Calculadora de Espacio y Bitrate para Amazon", "fr": "📏 Calculateur de Débit et d'Espace Amazon",
        "de": "📏 Amazon Speicher- & Bitratenrechner", "pt": "📏 Calculadora de Espaço e Bitrate para Amazon",
        "ja": "📏 Amazon ビットレート & 容量計算ツール", "zh": "📏 亚马逊码率与存储容量计算器"
    },
    "util_pattern": {
        "it": "🎨 Generatore Test Pattern SMPTE & Tono 1kHz", "en": "🎨 SMPTE Test Pattern & 1kHz Tone Generator",
        "es": "🎨 Generador de Patrón de Prueba SMPTE y Tono 1kHz", "fr": "🎨 Générateur de Mire SMPTE et Tonalité 1kHz",
        "de": "🎨 SMPTE Testbild- & 1kHz-Tongenerator", "pt": "🎨 Gerador de Padrão de Teste SMPTE e Tom de 1kHz",
        "ja": "🎨 SMPTE カラーバー & 1kHz トーンジェネレーター", "zh": "🎨 SMPTE 测试图卡与 1kHz 校准音频发生器"
    },
    "menu_reports": {
        "it": "&Reportistica", "en": "&Reports", "es": "&Reportes", "fr": "&Rapports", "de": "&Berichte", "pt": "&Relatórios", "ja": "レポート(&R)", "zh": "报告(&R)"
    },
    "menu_rep_pdf": {
        "it": "📄 Genera Certificato PDF Ufficiale Amazon Prime", "en": "📄 Generate Official Amazon Prime PDF Certificate",
        "es": "📄 Generar Certificado PDF Oficial Amazon Prime", "fr": "📄 Générer Certificat PDF Officiel Amazon Prime",
        "de": "📄 Offizielles Amazon Prime PDF-Zertifikat erstellen", "pt": "📄 Gerar Certificado PDF Oficial Amazon Prime",
        "ja": "📄 Amazon Prime 公式 PDF 証明書を生成", "zh": "📄 生成亚马逊 Prime 官方 PDF 质检证书"
    },
    "menu_rep_json": {
        "it": "📦 Esporta Manifest Tecnico JSON", "en": "📦 Export Technical JSON Manifest",
        "es": "📦 Exportar Manifiesto Técnico JSON", "fr": "📦 Exporter Manifeste Technique JSON",
        "de": "📦 Technisches JSON-Manifest exportieren", "pt": "📦 Exportar Manifesto Técnico JSON",
        "ja": "📦 技術 JSON マニフェストをエクスポート", "zh": "📦 导出技术 JSON 清单"
    },
    "menu_rep_csv": {
        "it": "📊 Esporta Tabella Errori CSV", "en": "📊 Export Issues Table CSV",
        "es": "📊 Exportar Tabla de Errores CSV", "fr": "📊 Exporter Tableau d'Erreurs CSV",
        "de": "📊 Fehlertabelle als CSV exportieren", "pt": "📊 Exportar Tabela de Erros CSV",
        "ja": "📊 エラー一覧 CSV をエクスポート", "zh": "📊 导出问题清单 CSV"
    },
    "menu_language": {
        "it": "🌐 &Lingua", "en": "🌐 &Language", "es": "🌐 &Idioma", "fr": "🌐 &Langue", "de": "&Sprache", "pt": "🌐 &Idioma", "ja": "🌐 言語(&L)", "zh": "🌐 语言(&L)"
    },
    "menu_help": {
        "it": "&Aiuto", "en": "&Help", "es": "&Ayuda", "fr": "&Aide", "de": "&Hilfe", "pt": "&Ajuda", "ja": "ヘルプ(&H)", "zh": "帮助(&H)"
    },
    "menu_help_guide": {
        "it": "📚 Guida agli Standard Amazon Prime Video", "en": "📚 Amazon Prime Video Standards Guide",
        "es": "📚 Guía de Estándares de Amazon Prime Video", "fr": "📚 Guide des Standards Amazon Prime Video",
        "de": "📚 Amazon Prime Video Standard-Leitfaden", "pt": "📚 Guia de Padrões do Amazon Prime Video",
        "ja": "📚 Amazon Prime Video 納品規格ガイド", "zh": "📚 亚马逊 Prime Video 交付规范指南"
    },
    "menu_about": {
        "it": "🛡️ Informazioni su PrimeQC Master...", "en": "🛡️ About PrimeQC Master...",
        "es": "🛡️ Acerca de PrimeQC Master...", "fr": "🛡️ À propos de PrimeQC Master...",
        "de": "🛡️ Über PrimeQC Master...", "pt": "🛡️ Sobre o PrimeQC Master...",
        "ja": "🛡️ PrimeQC Master について...", "zh": "🛡️ 关于 PrimeQC Master..."
    },

    # Main Screen Controls
    "lbl_profile": {
        "it": "Profilo Amazon:", "en": "Amazon Profile:", "es": "Perfil Amazon:", "fr": "Profil Amazon:", "de": "Amazon-Profil:", "pt": "Perfil Amazon:", "ja": "Amazonプロファイル:", "zh": "亚马逊配置:"
    },
    "btn_start_qc": {
        "it": "⚡ START QC INSPECTION", "en": "⚡ START QC INSPECTION", "es": "⚡ INICIAR INSPECCIÓN QC", "fr": "⚡ DÉMARRER INSPECTION QC",
        "de": "⚡ QC-INSPEKTION STARTEN", "pt": "⚡ INICIAR INSPEÇÃO QC", "ja": "⚡ QC検査を開始", "zh": "⚡ 开始质检分析"
    },
    "drop_prompt": {
        "it": "Trascina qui il file Master Video (.mov, .mp4, .mxf, .ts) o clicca per sfogliare",
        "en": "Drag & drop Master Video file (.mov, .mp4, .mxf, .ts) or click to browse",
        "es": "Arrastra aquí el archivo Master de Video (.mov, .mp4, .mxf, .ts) o haz clic para explorar",
        "fr": "Glissez-déposez le fichier Master Vidéo (.mov, .mp4, .mxf, .ts) ou cliquez pour parcourir",
        "de": "Master-Videodatei (.mov, .mp4, .mxf, .ts) hierher ziehen oder zum Durchsuchen klicken",
        "pt": "Arraste aqui o arquivo Master de Vídeo (.mov, .mp4, .mxf, .ts) ou clique para procurar",
        "ja": "ここにマスタービデオファイル (.mov, .mp4, .mxf, .ts) をドラッグ＆ドロップ、またはクリックして選択",
        "zh": "将视频母版文件 (.mov, .mp4, .mxf, .ts) 拖拽至此处或点击浏览"
    },

    # Tabs
    "tab_prime_report": {
        "it": "📋 Report Ufficiale Amazon Prime", "en": "📋 Official Amazon Prime Report",
        "es": "📋 Reporte Oficial Amazon Prime", "fr": "📋 Rapport Officiel Amazon Prime",
        "de": "📋 Offizieller Amazon Prime Bericht", "pt": "📋 Relatório Oficial Amazon Prime",
        "ja": "📋 Amazon Prime 公式レポート", "zh": "📋 亚马逊 Prime 官方质检报告"
    },
    "tab_checkpoints": {
        "it": "📊 Tabella Checkpoint & Anomaly Log", "en": "📊 Checkpoint Table & Anomaly Log",
        "es": "📊 Tabla de Puntos de Control y Registro", "fr": "📊 Tableau des Points de Contrôle",
        "de": "📊 Prüfpunkte & Anomalie-Protokoll", "pt": "📊 Tabela de Verificação e Log",
        "ja": "📊 検査項目 & 異常ログ一覧", "zh": "📊 检查项清单与异常日志"
    },
    "tab_audio_studio": {
        "it": "🔊 Studio Audio & Radar Loudness", "en": "🔊 Audio Studio & Loudness Radar",
        "es": "🔊 Estudio de Audio y Radar Loudness", "fr": "🔊 Studio Audio et Radar Loudness",
        "de": "🔊 Tonstudio & Loudness-Radar", "pt": "🔊 Estúdio de Áudio e Radar Loudness",
        "ja": "🔊 音声スタジオ & ラウドネスメーター", "zh": "🔊 音频工作室与响度雷达"
    },
    "tab_frame_inspector": {
        "it": "👁️ Ispettore Fotogrammi & Player", "en": "👁️ Frame Inspector & Player",
        "es": "👁️ Inspector de Fotogramas y Reproductor", "fr": "👁️ Inspecteur d'Images et Lecteur",
        "de": "👁️ Frame-Inspektor & Player", "pt": "👁️ Inspetor de Quadros e Player",
        "ja": "👁️ フレームインスペクター & プレーヤー", "zh": "👁️ 逐帧检测与播放器"
    },
    "tab_remediation": {
        "it": "🔧 Guida Correzione NLE & FFmpeg", "en": "🔧 NLE & FFmpeg Fix Guide",
        "es": "🔧 Guía de Corrección NLE y FFmpeg", "fr": "🔧 Guide de Correction NLE & FFmpeg",
        "de": "🔧 NLE- & FFmpeg-Korrekturanleitung", "pt": "🔧 Guia de Correção NLE e FFmpeg",
        "ja": "🔧 NLE / FFmpeg 修正ガイド", "zh": "🔧 剪辑软件与 FFmpeg 修复指南"
    },

    # Status Messages & Verdicts
    "verdict_pass": {
        "it": "APPROVATO (ACCEPTED) - CONFORME PER LA DISTRIBUZIONE SU AMAZON PRIME",
        "en": "ACCEPTED - FULLY COMPLIANT FOR AMAZON PRIME VIDEO DELIVERY",
        "es": "APROBADO (ACCEPTED) - CONFORME PARA DISTRIBUCIÓN EN AMAZON PRIME",
        "fr": "APPROUVÉ (ACCEPTED) - CONFORME POUR LA DISTRIBUTION AMAZON PRIME",
        "de": "BESTANDEN (ACCEPTED) - VOLLSTÄNDIG KONFORM FÜR AMAZON PRIME",
        "pt": "APROVADO (ACCEPTED) - CONFORME PARA DISTRIBUIÇÃO NO AMAZON PRIME",
        "ja": "合格 (ACCEPTED) - Amazon Prime Video 納品基準に完全適合",
        "zh": "通过 (ACCEPTED) - 完全符合亚马逊 Prime Video 发行规范"
    },
    "verdict_fail": {
        "it": "RIGETTATO (REJECTED) - NON CONFORME AGLI STANDARD AMAZON PRIME",
        "en": "REJECTED - OUT OF SPECIFICATION FOR AMAZON PRIME VIDEO",
        "es": "RECHAZADO (REJECTED) - FUERA DE ESPECIFICACIÓN PARA AMAZON PRIME",
        "fr": "REJETÉ (REJECTED) - HORS SPÉCIFICATIONS AMAZON PRIME",
        "de": "ABGELEHNT (REJECTED) - NICHT KONFORM MIT AMAZON PRIME STANDARDS",
        "pt": "REJEITADO (REJECTED) - FORA DE ESPECIFICAÇÃO PARA AMAZON PRIME",
        "ja": "不合格 (REJECTED) - Amazon Prime Video 納品基準に不適合",
        "zh": "驳回 (REJECTED) - 不符合亚马逊 Prime Video 质量标准"
    },
    "verdict_warn": {
        "it": "REVISIONE CONSIGLIATA (WARNING) - AVVISI RILEVATI",
        "en": "REVIEW RECOMMENDED (WARNING) - NON-BLOCKING ISSUES DETECTED",
        "es": "REVISIÓN RECOMENDADA (WARNING) - AVISOS DETECTADOS",
        "fr": "RÉVISION RECOMMANDÉE (WARNING) - AVERTISSEMENTS DÉTECTÉS",
        "de": "ÜBERPRÜFUNG EMPFOHLEN (WARNING) - WARNUNGEN GEFUNDEN",
        "pt": "REVISÃO RECOMENDADA (WARNING) - AVISOS DETECTADOS",
        "ja": "要確認 (WARNING) - 軽微な警告が検出されました",
        "zh": "建议复核 (WARNING) - 检测到非阻塞性警告"
    },
    "why_reject_title": {
        "it": "❓ Perché Amazon Prime rigetta questo file:",
        "en": "❓ Why Amazon Prime Video rejects this file:",
        "es": "❓ Por qué Amazon Prime rechaza este archivo:",
        "fr": "❓ Pourquoi Amazon Prime rejette ce fichier:",
        "de": "❓ Warum Amazon Prime diese Datei ablehnt:",
        "pt": "❓ Por que o Amazon Prime rejeita este arquivo:",
        "ja": "❓ Amazon Prime がこのファイルを却下する理由:",
        "zh": "❓ 亚马逊 Prime 驳回此文件的原因:"
    },
    "how_fix_title": {
        "it": "🔧 Come correggerlo per passare il QC al 100%:",
        "en": "🔧 How to fix this to achieve 100% QC Pass:",
        "es": "🔧 Cómo corregirlo para pasar el QC al 100%:",
        "fr": "🔧 Comment corriger pour réussir le QC à 100%:",
        "de": "🔧 Wie Sie dies korrigieren, um 100% QC zu bestehen:",
        "pt": "🔧 Como corrigir para atingir 100% de aprovação:",
        "ja": "🔧 100% QC 合格するための修正方法:",
        "zh": "🔧 如何修复以达到 100% 质检通过率:"
    },
    "score_label": {
        "it": "Punteggio Conformità", "en": "Compliance Score", "es": "Puntuación de Conformidad",
        "fr": "Score de Conformité", "de": "Konformitätswert", "pt": "Pontuação de Conformidade",
        "ja": "適合スコア", "zh": "合规得分"
    },
    "status_ready": {
        "it": "Pronto per l'ingestione. Seleziona o trascina un master video.",
        "en": "Ready for ingestion. Select or drag & drop a video master.",
        "es": "Listo para la ingesta. Selecciona o arrastra un master de video.",
        "fr": "Prêt pour l'ingestion. Sélectionnez ou glissez un master vidéo.",
        "de": "Bereit zur Aufnahme. Wählen Sie ein Video-Master aus.",
        "pt": "Pronto para ingestão. Selecione ou arraste um master de vídeo.",
        "ja": "準備完了。ビデオマスターを選択またはドラッグ＆ドロップしてください。",
        "zh": "就绪。请选择或拖入视频母版文件。"
    }
}


class I18nManager:
    """Singleton Internationalization manager."""
    _instance = None
    _current_lang = "it"
    _listeners: List[Callable[[str], None]] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18nManager, cls).__new__(cls)
            cls._instance._load_saved_lang()
        return cls._instance

    def _load_saved_lang(self):
        config_path = os.path.join(os.path.expanduser("~"), ".primeqc", "settings.json")
        if os.path.isfile(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    saved = data.get("language", "it")
                    if saved in LANGUAGES:
                        self._current_lang = saved
            except Exception:
                self._current_lang = "it"

    def get_current_language(self) -> str:
        return self._current_lang

    def set_language(self, lang_code: str):
        if lang_code in LANGUAGES and lang_code != self._current_lang:
            self._current_lang = lang_code
            self._save_lang(lang_code)
            # Notify listeners
            for cb in self._listeners:
                try:
                    cb(lang_code)
                except Exception:
                    pass

    def _save_lang(self, lang_code: str):
        config_dir = os.path.join(os.path.expanduser("~"), ".primeqc")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "settings.json")
        data = {}
        if os.path.isfile(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data["language"] = lang_code
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def subscribe(self, callback: Callable[[str], None]):
        """Subscribes a callback function when language changes."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unsubscribe(self, callback: Callable[[str], None]):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def translate(self, key: str, fallback: str = "") -> str:
        """Retrieves translated text for given key."""
        entry = TRANSLATIONS.get(key)
        if entry:
            return entry.get(self._current_lang, entry.get("en", fallback or key))
        return fallback or key


# Global helper function for fast translation lookup
def _t(key: str, fallback: str = "") -> str:
    return I18nManager().translate(key, fallback)
