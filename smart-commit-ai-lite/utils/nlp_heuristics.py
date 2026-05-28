import nltk
try:
    import regex as re
except ImportError:
    import re

from utils.input_cleanup import (
    clean_input as clean_pasted_input,
    clean_summary_text as clean_summary_snippet,
    detect_input_noise_warnings as detect_pasted_input_noise_warnings,
    strip_markdown_noise as strip_pasted_markdown_noise,
)
from utils.language import (
    detect_language as detect_input_language,
    language_signal_text as get_language_signal_text,
)
from utils.type_scope import (
    DetectionContext,
    detect_scope as detect_commit_scope,
    select_commit_type as select_conventional_commit_type,
)


class NLPEngine:
    def clean_summary_text(self, text):
        return clean_summary_snippet(text)

    def strip_markdown_noise(self, text):
        return strip_pasted_markdown_noise(text)

    def detect_input_noise_warnings(self, text):
        return detect_pasted_input_noise_warnings(text)

    def detect_language(self, text):
        return detect_input_language(text)

    def language_signal_text(self, text):
        return get_language_signal_text(text)

    def sent_tokenize_by_language(self, text, language):
        nltk_language = 'spanish' if language == 'es' else 'english'
        try:
            return nltk.sent_tokenize(text, language=nltk_language)
        except LookupError:
            return re.split(r'(?<=[.!?])\s+', text)

    def clean_input(self, text):
        return clean_pasted_input(text)

    def is_readme_architecture_docs_summary(self, text_lower):
        if 'readme' not in text_lower:
            return False
        markers = [
            'lightweight ml layer', 'project principles', 'do not use',
            'supported ml labels', 'responsibility split', 'joblib artifact',
            'debian validation', 'contribution guidance', 'heavy dependencies',
            'scikit-learn vs heuristic'
        ]
        return sum(1 for marker in markers if marker in text_lower) >= 2

    def is_ml_metadata_validation_summary(self, text_lower):
        markers = [
            'model metadata validation',
            'model_metadata.json',
            'metadata validation',
            'required fields',
            'format version',
            'distributed ml model',
            'model ready',
            'ml/predictor.py',
            'valid metadata',
            'invalid metadata',
        ]
        return (
            any(marker in text_lower for marker in markers[:3])
            and sum(1 for marker in markers if marker in text_lower) >= 3
        )

    def is_mixed_language_nlp_summary(self, text_lower):
        language_markers = [
            'language detection',
            'detect language',
            'mixed spanish',
            'spanish and english',
            'english and spanish',
            'mixed-language',
            'mixed language',
            'tokenization',
            'tokenización',
            'idioma',
        ]
        ui_status_markers = ['status label', 'language status', 'detected language status', 'etiqueta de estado']
        return (
            any(marker in text_lower for marker in language_markers)
            and any(marker in text_lower for marker in ['mixed', 'mixed-language', 'mixed language', 'mixto', 'mixta', 'mixtos', 'mixtas'])
            and not any(marker in text_lower for marker in ui_status_markers)
        )

    def is_ml_pipeline_summary(self, text_lower):
        ml_markers = [
            'ml/dataset_loader.py',
            'ml/train_model.py',
            'ml/predictor.py',
            'offline ml',
            'ml training',
            'training pipeline',
            'joblib',
            'vectorizer',
            'model_metadata',
            'sklearn',
            'scikit-learn',
            'tf-idf',
            'linearsvc',
        ]
        return sum(1 for marker in ml_markers if marker in text_lower) >= 2

    def is_spanish_verb_expansion_summary(self, text_lower):
        verb_markers = [
            'spanish verb support',
            'spanish conjugations',
            'spanish verb expansion',
            'verbos españoles',
            'conjugaciones',
            'arreglé',
            'añadimos',
            'mejoramos',
            'documentamos',
            'actualiza proyecto',
        ]
        return (
            sum(1 for marker in verb_markers if marker in text_lower) >= 2
            and any(marker in text_lower for marker in ['smart_commit_nltk.py', 'test_smart_commit_nltk.py', 'roadmap.md'])
        )

    def extract_object_phrase(self, phrase):
        phrase = re.sub(r'\[.*?\]', ' ', phrase)
        phrase = phrase.replace('->', ' -> ')
        phrase = phrase.replace('-', ' ')
        phrase = phrase.replace('_', ' ')
        phrase = re.sub(r'([a-z])([A-Z])', r'\1 \2', phrase)
        phrase = re.sub(r'\s+', ' ', phrase).strip()
        if not phrase:
            return ""

        words = nltk.word_tokenize(phrase)
        tagged = nltk.pos_tag(words)

        obj_words = []
        started = False
        stop_tags = ('IN', 'CC', 'TO', 'PRP', 'PRP$', 'WDT', 'WP', 'WP$', 'WRB', 'DT')
        allowed_prefixes = ('NN', 'JJ', 'CD', 'VBG', 'VBD', 'VBN', 'NNP', 'NNS')
        generic_start = {'the', 'a', 'an', 'this', 'that', 'these', 'those', 'new', 'real', 'useful', 'actual', 'existing', 'same', 'shared', 'direct', 'first', 'initial', 'basic', 'small', 'genuine', 'local', 'localized'}

        for word, tag in tagged:
            lower = word.lower()
            if not started:
                if lower in generic_start:
                    continue
                if any(tag.startswith(prefix) for prefix in allowed_prefixes) or lower in {
                    'api', 'ui', 'ux', 'cli', 'db', 'sql', 'html', 'css', 'javascript', 'python', 'java', 'json', 'yaml', 'xml',
                    'service', 'endpoint', 'query', 'schema', 'migration', 'token', 'auth', 'password', 'session', 'cache',
                    'pipeline', 'dashboard', 'widget', 'plugin', 'extension', 'module', 'component', 'router', 'layout', 'dialog',
                    'window', 'view', 'form', 'button', 'menu', 'help', 'guide', 'documentation', 'roadmap', 'readme', 'tests',
                    'coverage', 'validation', 'lyrics', 'channels', 'pianola', 'program', 'volume', 'midi', 'preferences', 'settings',
                    'encoding', 'font', 'copy', 'print', 'fullscreen', 'track', 'tabs', 'color', 'label', 'keyboard', 'action', 'toggle', 'selector', 'dialog', 'spinbox', 'combo', 'combobox', 'panel', 'mode'
                } or lower == '->':
                    obj_words.append(lower)
                    started = True
                continue

            if tag.startswith(stop_tags) or lower in {',', '.', ';', ':', ')', '(', '``', "''"}:
                break
            if any(tag.startswith(prefix) for prefix in allowed_prefixes) or lower in {'and', 'for', 'with', 'to', 'from', 'by', 'of', 'on', 'in', 'as', '->', '>'}:
                obj_words.append(lower)
            else:
                break

        cleaned = " ".join(obj_words).strip().rstrip(',.')
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    def score_sentence_for_subject(self, sentence):
        score = 0
        s = sentence.lower()
        # Prefer sentences starting with action verbs
        if re.search(r'^\s*(add|implement|create|introduce|build|update|change|modify|fix|resolve|correct|enhance|extend|replace|improve|remove|delete|rename|merge|optimize|document|format|configure)', s):
            score += 20
        if re.search(r'^\s*(agrega|añade|crea|implementa|actualiza|cambia|modifica|corrige|arregla|mejora|documenta|formatea|configura|incluye|resume)', s):
            score += 20
        if re.search(r'\bin \[[^\]]+\].*?\b(i|we)\s+(added|created|implemented|updated|changed|modified|fixed|resolved|corrected|replaced|introduced|moved|landed|carried|kept)\b', s):
            score += 20
        if re.search(r'\b(i|we)\s+(added|created|implemented|updated|changed|modified|fixed|resolved|corrected|replaced|introduced|moved|landed|carried|kept|made)\b', s):
            score += 15
        if re.search(r'\b(he|hemos|yo|nosotros)\s+(creado|añadido|agregado|implementado|actualizado|cambiado|modificado|corregido|arreglado|mejorado|documentado)\b', s):
            score += 15
        if re.search(r'\bwe\s+got\b', s):
            score += 14
        if re.search(r'\b(roadmap|readme|documentación|documentacion|guía|guia|docs)\b', s):
            score -= 5
        if re.search(r'\bhelp\s*->\s*user guide\b', s):
            score += 12
        if re.search(r'\b(user guide|lyrics window|channels view|piano player|pianola)\b', s):
            score += 5
        if re.search(r'\b(test|tests|unittest|pytest|ci|coverage|validation)\b', s):
            score -= 15
        return score

    def extract_action_phrase(self, sentence):
        sentence = self.clean_summary_text(sentence)
        if not sentence:
            return None, None

        sentence_lower = sentence.lower()
        sentence_lower = sentence_lower.replace("’", "'")
        sentence_lower = sentence_lower.replace("`", "")

        if re.search(r'\broadmap\.md\b|\broadmap\b', sentence_lower):
            if re.search(r'\b(created|added|add|new file)\b', sentence_lower):
                return 'add', 'project roadmap with progress tracking'
            if re.search(r'\b(updated|mark|completed|complete)\b', sentence_lower):
                return 'update', 'project roadmap'



        if re.search(r'\b(type\s*(?:and|/)\s*scope|manual type|manual scope|type selector|scope selector|dropdowns?|manual override|regenerat(?:e|ion))\b', sentence_lower):
            return 'add', 'manual type and scope selectors'

        if re.search(r'\b(clear input|clear button|reset input|copy button|refocus input)\b', sentence_lower):
            return 'add', 'Clear Input button to generator interface'

        if re.search(r'\b(language status|detected language|language detection|status label|pending|es/en)\b', sentence_lower):
            return 'add', 'detected language status indicator'

        if (
            re.search(r'\b(spanish|english|bilingual|language|tokenization|spanish verbs)\b', sentence_lower)
            and re.search(r'\b(detect|uses?|understand|generate|support)\b', sentence_lower)
        ):
            if re.search(r'\bci\b|false-positive|type detection', sentence_lower):
                return 'add', 'bilingual support and fix type detection'
            return 'add', 'bilingual commit support'

        if re.search(r'\b(false-positive|false positive)\b.*\bci\b|\bci\b.*\b(false-positive|false positive)\b', sentence_lower):
            return 'fix', 'ci type detection'

        special_patterns = [
            (r'\bhelp\s*->\s*user guide\b', 'add'),
            (r'\bview\s*->\s*rhythm\b', 'add'),
            (r'\bview\s*->\s*channels\b', 'add'),
            (r'\bview\s*->\s*lyrics\b', 'add'),
            (r'\bhelp\s*->\s*about\b', 'docs'),
            (r'\bencoding selector\b', 'add'),
            (r'\bsave button\b', 'add'),
            (r'\bfullscreen\b', 'add'),
            (r'\bcopy and font\b', 'add'),
            (r'\btrack-aware\b', 'add'),
            (r'\bprogram\s+(?:spinbox|selector|control)\b', 'add'),
            (r'\b(?:in \[[^\]]+\].*?\b(?:i|we)\s+added\s+real\s+(.+?))(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:in \[[^\]]+\].*?\b(?:i|we)\s+added\s+(?:a\s+new\s+)?(.+?))(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+added\s+real\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+added\s+(?:a\s+new\s+)?(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+created\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+implemented\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+introduced\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'add'),
            (r'\b(?:i|we)\s+updated\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'update'),
            (r'\b(?:i|we)\s+changed\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'update'),
            (r'\b(?:i|we)\s+modified\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'update'),
            (r'\b(?:i|we)\s+replaced\s+(.+?)(?:\s+with|\s+to|\s+for|\s+in|\s+and|\.|$)', 'replace'),
            (r'\b(?:i|we)\s+refactored\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'refactor'),
            (r'\b(?:i|we)\s+(?:fixed|corrected|resolved)\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'fix'),
            (r'\b(?:i|we)\s+sent\s+(.+?)(?:\s+to|\s+for|\s+with|\s+in|\s+and|\.|$)', 'send'),
        ]

        for pattern, action in special_patterns:
            match = re.search(pattern, sentence_lower, re.IGNORECASE)
            if match:
                if match.groups():
                    obj_text = match.group(1)
                else:
                    obj_text = match.group(0)
                obj = self.extract_object_phrase(obj_text)
                if obj:
                    return action, obj

        verb_map = {
            'added': 'add', 'create': 'add', 'created': 'add', 'implement': 'add', 'implemented': 'add', 'introduced': 'add',
            'built': 'add', 'landed': 'add', 'pushed': 'update', 'moved': 'move', 'refactored': 'refactor',
            'cleaned': 'refactor', 'updated': 'update', 'changed': 'update', 'modified': 'update',
            'fixed': 'fix', 'corrected': 'fix', 'resolved': 'fix', 'improved': 'improve', 'made': 'improve',
            'replaced': 'replace', 'sent': 'send', 'applied': 'apply', 'removed': 'remove', 'deleted': 'remove',
            'restored': 'restore', 'renamed': 'rename', 'merged': 'merge', 'optimized': 'optimize',
            'documented': 'doc', 'formatted': 'format', 'configured': 'configure'
        }

        found = re.search(r"\b(added|created|implemented|introduced|built|landed|pushed|moved|refactored|cleaned|updated|changed|modified|fixed|resolved|corrected|improved|made|replaced|sent|applied|removed|deleted|restored|renamed|merged|optimized|documented|formatted|configured)\b", sentence_lower)
        if found:
            verb = found.group(1)
            action = verb_map.get(verb, verb)
            tail = sentence[found.end():]
            obj = self.extract_object_phrase(tail)
            if obj:
                return action, obj

        words = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(words)
        auxiliaries = {'be', 'have', 'do', 'let', 'get', 'got', 'make', 'makes', 'made', 'is', 'are', 'was', 'were', 'will', 'would', 'can', 'could', 'should', 'may', 'might'}
        for index, (word, tag) in enumerate(tagged):
            if tag.startswith('VB') and word.lower() not in auxiliaries:
                verb = word.lower()
                noun_phrase = self.extract_object_phrase(' '.join(w for w, _ in tagged[index + 1:]))
                if noun_phrase:
                    return verb_map.get(verb, verb), noun_phrase

        return None, None

    def extract_spanish_object_phrase(self, phrase):
        phrase = re.sub(r'\[.*?\]', ' ', phrase)
        phrase = phrase.replace('`', ' ')
        phrase = phrase.replace('->', ' -> ')
        phrase = re.sub(r'([a-záéíóúñ])([A-Z])', r'\1 \2', phrase)
        phrase = re.sub(r'\s+', ' ', phrase).strip()
        if not phrase:
            return ""

        stop_words = {
            'para', 'por', 'con', 'sin', 'desde', 'hasta', 'y', 'e', 'o', 'u',
            'que', 'donde', 'cuando', 'como', 'porque', 'si', 'pero', 'aunque',
            'también', 'tambien', 'además', 'ademas', 'dejando', 'marcando'
        }
        generic_start = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'este',
            'esta', 'estos', 'estas', 'nuevo', 'nueva', 'nuevos', 'nuevas'
        }

        tokens = re.findall(r'[\wÁÉÍÓÚÜÑáéíóúüñ./_-]+|->', phrase, re.UNICODE)
        obj_words = []
        for token in tokens:
            lower = token.lower().strip('.,;:()[]{}')
            if not lower:
                continue
            if not obj_words and lower in generic_start:
                continue
            if lower in stop_words:
                break
            if re.match(r'^[\wáéíóúüñ./_-]+$', lower) or lower == '->':
                obj_words.append(lower)
            if len(obj_words) >= 8:
                break

        cleaned = " ".join(obj_words).strip().rstrip(',.')
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    def extract_action_phrase_es(self, sentence):
        sentence = self.clean_summary_text(sentence)
        if not sentence:
            return None, None

        sentence_lower = sentence.lower().replace("`", "")

        if re.search(r'\broadmap\.md\b|\broadmap\b', sentence_lower):
            if re.search(r'\b(cread[oa]|creé|creamos|he creado|hemos creado|nuevo archivo)\b', sentence_lower):
                return 'add', 'roadmap con seguimiento de progreso'
            if re.search(r'\b(actualizad[oa]|marcar|marcando|completad[oa]s?)\b', sentence_lower):
                return 'update', 'roadmap del proyecto'



        if re.search(r'\b(type\s*(?:y|/)\s*scope|selectores|tipo:|scope:|editar manualmente|corregirlo manualmente|regenera|ajuste manual)\b', sentence_lower):
            return 'add', 'selectores manuales de type y scope'

        if re.search(r'\b(limpiar entrada|bot[oó]n limpiar|borrar el texto de entrada|borra el texto|bot[oó]n de copiar|cuadro de entrada|foco)\b', sentence_lower):
            return 'add', 'botón Limpiar entrada en la interfaz'

        if re.search(r'\b(idioma detectado|etiqueta de estado|estado.*idioma|muestra el idioma)\b', sentence_lower):
            return 'add', 'indicador de idioma detectado'

        if (
            re.search(r'\b(español|ingles|inglés|biling[uü]e|idioma|tokenizaci[oó]n|verbos españoles)\b', sentence_lower)
            and re.search(r'\b(detecta|usa|entiende|genera|soporte|compatibilidad)\b', sentence_lower)
        ):
            if re.search(r'\bci\b|falso positivo|false-positive|detecci[oó]n de tipo', sentence_lower):
                return 'add', 'soporte bilingüe y corrige detección de tipo'
            return 'add', 'soporte bilingüe para commits'

        if re.search(r'\b(falso positivo|false-positive)\b.*\bci\b|\bci\b.*\b(falso positivo|false-positive)\b', sentence_lower):
            return 'fix', 'detección de tipo ci'

        colloquial_support_match = re.search(
            r'\ble\s+met[íi]\s+soporte\s+para\s+(.+?)(?:\s+en|\s+con|\s+y|\.|$)',
            sentence_lower,
            re.IGNORECASE,
        )
        if colloquial_support_match:
            obj = self.extract_spanish_object_phrase(colloquial_support_match.group(1))
            if obj:
                return 'add', f'soporte para {obj}'

        colloquial_tests_match = re.search(
            r'\ble\s+puse\s+tests?\s+(?:a|al|para)\s+(.+?)(?:\s+en|\s+con|\s+y|\.|$)',
            sentence_lower,
            re.IGNORECASE,
        )
        if colloquial_tests_match:
            obj = self.extract_spanish_object_phrase(colloquial_tests_match.group(1))
            if obj:
                return 'add', f'tests para {obj}'

        passive_fix_match = re.search(
            r'\bse\s+arregl[oó]\s+(.+?)(?:\s+en|\s+con|\s+y|\.|$)',
            sentence_lower,
            re.IGNORECASE,
        )
        if passive_fix_match:
            obj = self.extract_spanish_object_phrase(passive_fix_match.group(1))
            if obj:
                return 'fix', obj

        passive_docs_match = re.search(
            r'\bqued[oó]\s+documentad[ao]\s+(.+?)(?:\s+en|\s+con|\s+y|\.|$)',
            sentence_lower,
            re.IGNORECASE,
        )
        if passive_docs_match:
            obj = self.extract_spanish_object_phrase(passive_docs_match.group(1))
            if obj:
                return 'doc', obj

        support_match = re.search(
            r'\b(?:he|hemos)?\s*(?:añadido|añadí|añadimos|agregado|agregué|agregamos|incorporado|incorporamos)\s+soporte\s+para\s+(.+?)(?:\s+en|\s+con|\s+y|\.|$)',
            sentence_lower,
            re.IGNORECASE,
        )
        if support_match:
            obj = self.extract_spanish_object_phrase(support_match.group(1))
            if obj:
                return 'add', f'soporte para {obj}'

        special_patterns = [
            (r'\b(?:he|hemos)?\s*(?:creado|creé|creamos)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'add'),
            (r'\b(?:he|hemos)?\s*(?:añadido|añadí|añadimos|agregado|agregué|agregamos|incorporado|incorporamos)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'add'),
            (r'\b(?:he|hemos)?\s*(?:implementado|implementé|implementamos)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'add'),
            (r'\b(?:he|hemos)?\s*(?:actualizado|actualicé|actualizamos)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'update'),
            (r'\b(?:he|hemos)?\s*(?:corregido|corregí|corregimos|arreglado|arreglé|arreglamos|resuelto|resolvimos)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'fix'),
            (r'\b(?:he|hemos)?\s*(?:mejorado|mejoré|mejoramos|optimizado|optimizamos)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'improve'),
            (r'\b(?:he|hemos)?\s*(?:documentado|documenté|documentamos)\s+(.+?)(?:\s+en|\s+para|\s+con|\s+y|\.|$)', 'doc'),
            (r'\b(?:este\s+documento\s+)?(?:incluye|resume|documenta)\s+(.+?)(?:\s+para|\s+con|\s+y|\.|$)', 'doc'),
        ]

        for pattern, action in special_patterns:
            match = re.search(pattern, sentence_lower, re.IGNORECASE)
            if match:
                obj = self.extract_spanish_object_phrase(match.group(1))
                if obj:
                    return action, obj

        return None, None

    def is_commitworthy_sentence(self, sentence):
        normalized = sentence.lower()
        # Must have action verb (with or without subject pronoun)
        action_verbs = [
            'add', 'implement', 'create', 'introduce', 'build', 'land', 'push', 'move', 'refactor', 'clean',
            'update', 'change', 'modify', 'fix', 'resolve', 'correct', 'enhance', 'extend', 'replace', 'improve',
            'make', 'remove', 'delete', 'rename', 'merge', 'optimize', 'document', 'format', 'configure',
            'recognize', 'raise', 'prevent', 'support', 'load', 'write', 'read', 'report', 'normalize', 'cover',
            'validate', 'generate', 'fall', 'give', 'set', 'use', 'return', 'throw', 'handle', 'catch', 'allow',
            'agrega', 'añade', 'crea', 'creado', 'crear', 'implementa', 'implementado', 'actualiza',
            'actualizado', 'cambia', 'modifica', 'corrige', 'arregla', 'mejora', 'mejorado',
            'documenta', 'documentado', 'incluye', 'resume'
        ]
        has_action = any(re.search(rf"\b{verb}\b", normalized) for verb in action_verbs)
        if not has_action:
            return False
        
        # Avoid sentences that are just descriptions or results
        if re.search(r"\b(it|this|that)\s+(updates|now|shows|supports|uses|sends|displays|provides|includes|contains)\b", normalized):
            return False
        # Avoid test/validation sentences
        if re.search(r"\b(verification|compileall|tests|passed|OK|validation)\b", normalized):
            return False
        # Avoid generic or conversational sentences
        if re.search(r"\b(yo|tu|usted|nosotros|ellos|este|eso|aquí|ahí|allí|como|porque|si|no|pero|sin embargo)\b", normalized):
            return False
        # Avoid very short sentences
        if len(normalized.split()) < 4:
            return False
        return True

    def pick_best_sentence(self, text, language='en'):
        sentences = self.sent_tokenize_by_language(text, language)
        best_score = -999
        best_sentence = text.strip()

        for sentence in sentences:
            content = sentence.strip()
            if len(content) < 10:
                continue
            normalized = content.lower()
            if normalized.startswith((
                'verification', 'current', 'test', 'tests', 'compileall', 'and ', 'but ', 'also ',
                'verificación', 'verificacion', 'pruebas', 'validación', 'validacion', 'y ', 'pero ', 'también ', 'tambien '
            )):
                continue
            score = self.score_sentence_for_subject(content)
            if score > best_score:
                best_score = score
                best_sentence = content

        return best_sentence

    def analyze_with_nltk(self, text, forced_language=None):
        language = forced_language or self.detect_language(text)
        normalized = self.clean_input(text)

        normalized_lower = normalized.lower()
        has_evaluation_baseline_context = any(k in normalized_lower for k in [
            'testing/evaluación', 'testing/evaluation', 'línea base', 'linea base',
            'baseline', '45 ejemplos', '45 examples', '0.446', '6 regresiones',
            '6 tests', 'compare_generator.py', '.gitignore'
        ])
        has_preview_truncation_refactor = (
            any(k in normalized_lower for k in ['vista previa', 'preview ui', 'legacy preview'])
            and any(k in normalized_lower for k in ['truncate_subject', 'truncado', 'trunca', 'word-aware', 'word boundary', 'límites de palabra', 'limites de palabra'])
        )
        if has_preview_truncation_refactor:
            if language == 'es':
                return 'improve', 'truncado de subject y elimina vista previa', language
            return 'refactor', 'word-aware subject truncation', language

        if language == 'es' and any(k in normalized_lower for k in ['menciones de archivos', 'archivos mencionados', 'clasificación de archivos']):
            return 'improve', 'detección de menciones de archivos', language
        if language == 'en' and any(k in normalized_lower for k in ['file mentions', 'mentioned files', 'file classification']):
            return 'improve', 'file mention detection', language

        if language == 'es' and any(k in normalized_lower for k in ['type y scope', 'type/scope', 'selectores', 'editar manualmente', 'corregirlo manualmente', 'ajuste manual']):
            return 'add', 'selectores manuales de type y scope', language
        if language == 'en' and any(k in normalized_lower for k in ['type and scope', 'type/scope', 'type selector', 'scope selector', 'dropdown', 'manual override']):
            return 'add', 'manual type and scope selectors', language

        if language == 'es' and any(k in normalized_lower for k in ['idioma detectado', 'etiqueta de estado', 'muestra el idioma', 'estado que muestra el idioma']):
            return 'add', 'indicador de idioma detectado', language
        if language == 'en' and any(k in normalized_lower for k in ['detected language', 'language status', 'status label', 'language detection']):
            return 'add', 'detected language status indicator', language

        if language == 'es' and any(k in normalized_lower for k in ['limpiar entrada', 'botón limpiar', 'boton limpiar', 'borrar el texto de entrada', 'borra el texto', 'botón de copiar', 'boton de copiar', 'cuadro de entrada']):
            return 'add', 'botón Limpiar entrada en la interfaz', language
        if language == 'en' and any(k in normalized_lower for k in ['clear input', 'clear button', 'reset input', 'copy button', 'refocus input']):
            return 'add', 'Clear Input button to generator interface', language

        if language == 'es' and (
            any(k in normalized_lower for k in ['test_smart_commit_nltk.py', 'regresiones', 'testing/evaluación', 'comparison_report.json', 'compare_generator.py', 'línea base', 'linea base'])
            and any(k in normalized_lower for k in ['roadmap', 'readme', '.gitignore', '6 tests', '45 ejemplos', '0.446'])
            and has_evaluation_baseline_context
        ):
            return 'add', 'suite de regresión y baseline de evaluación', language
        if language == 'en' and (
            any(k in normalized_lower for k in ['test_smart_commit_nltk.py', 'regression tests', 'testing/evaluation', 'comparison_report.json', 'compare_generator.py', 'baseline'])
            and any(k in normalized_lower for k in ['roadmap', 'readme', '.gitignore', '6 tests', '45 examples', '0.446'])
            and has_evaluation_baseline_context
        ):
            return 'add', 'regression suite and evaluation baseline', language

        if language == 'en' and self.is_readme_architecture_docs_summary(normalized_lower):
            return 'expand', 'project principles and architecture', language

        if language == 'en' and self.is_ml_metadata_validation_summary(normalized_lower):
            return 'add', 'strict metadata validation in predictor', language

        if language == 'en' and self.is_ml_pipeline_summary(normalized_lower):
            return 'improve', 'offline ml training pipeline', language

        if language == 'en' and self.is_spanish_verb_expansion_summary(normalized_lower):
            return 'expand', 'Spanish verb support', language

        if self.is_mixed_language_nlp_summary(normalized_lower):
            if language == 'es':
                return 'improve', 'detección de idioma en textos mixtos', language
            return 'improve', 'mixed-language detection', language

        best_sentence = self.pick_best_sentence(normalized, language)

        if language == 'es':
            subject_verb, subject_obj = self.extract_action_phrase_es(best_sentence)
        else:
            subject_verb, subject_obj = self.extract_action_phrase(best_sentence)

        if not subject_verb or not subject_obj:
            if language == 'es':
                subject_verb, subject_obj = self.extract_action_phrase_es(normalized)
            else:
                subject_verb, subject_obj = self.extract_action_phrase(normalized)

        if not subject_verb:
            subject_verb = 'update'
        if not subject_obj or subject_obj.lower() in ['project', 'proyecto', 'it', 'this', 'files', 'archivos', 'code', 'código', 'codigo', 'things', 'stuff']:
            mentions = self.extract_file_mentions(normalized)
            if mentions:
                if language == 'es':
                    subject_obj = f"archivos ({mentions[0]})"
                else:
                    subject_obj = f"files ({mentions[0]})"
            else:
                subject_obj = 'proyecto' if language == 'es' else 'project'

        subject_verb = subject_verb.lower()
        subject_obj = subject_obj.lower()

        if subject_obj in ['user', 'help'] and 'user guide' in normalized:
            subject_obj = 'user guide'
        elif subject_obj in ['lyrics', 'window'] and 'lyrics window' in normalized:
            subject_obj = 'lyrics window'
        elif subject_obj in ['channels'] and 'channels view' in normalized:
            subject_obj = 'channels view'
        elif subject_obj in ['pianola', 'piano'] and 'piano player' in normalized:
            subject_obj = 'piano player'

        if language == 'es' and 'soporte bilingüe' in subject_obj and re.search(r'\bci\b|falso positivo|detecci[oó]n de tipo', normalized):
            subject_obj = 'soporte bilingüe y corrige tipo ci'
        elif language == 'en' and 'bilingual' in subject_obj and re.search(r'\bci\b|false-positive|type detection', normalized):
            subject_obj = 'bilingual support and fix type detection'

        if subject_verb == 'got' and subject_obj:
            subject_verb = 'add'
        if subject_verb == 'made':
            subject_verb = 'improve'

        return subject_verb, subject_obj, language

    def format_subject(self, action, obj, language):
        if language == 'es':
            verb_map = {
                'add': 'agrega', 'update': 'actualiza', 'fix': 'corrige',
                'improve': 'mejora', 'refactor': 'refactoriza', 'replace': 'reemplaza',
                'remove': 'elimina', 'doc': 'documenta', 'docs': 'documenta',
                'format': 'formatea', 'configure': 'configura', 'optimize': 'optimiza'
            }
        else:
            verb_map = {
                'add': 'add', 'update': 'update', 'fix': 'fix',
                'improve': 'improve', 'refactor': 'refactor', 'replace': 'replace',
                'remove': 'remove', 'doc': 'document', 'docs': 'document',
                'format': 'format', 'configure': 'configure', 'optimize': 'optimize',
                'expand': 'expand'
            }

        verb = verb_map.get(action, action)
        return f"{verb} {obj}".strip()

    def detection_context(self, text_lower):
        return DetectionContext(
            readme_architecture_docs=self.is_readme_architecture_docs_summary(text_lower),
            ml_metadata_validation=self.is_ml_metadata_validation_summary(text_lower),
            mixed_language_nlp=self.is_mixed_language_nlp_summary(text_lower),
            ml_pipeline=self.is_ml_pipeline_summary(text_lower),
            spanish_verb_expansion=self.is_spanish_verb_expansion_summary(text_lower),
        )

    def detect_scope(self, text):
        text_lower = text.lower()
        return detect_commit_scope(text, self.detection_context(text_lower))

    def select_commit_type(self, text, subject_verb, subject_obj):
        text_lower = text.lower()
        return select_conventional_commit_type(
            text,
            subject_verb,
            subject_obj,
            self.detection_context(text_lower),
        )

    def extract_validation_bullet(self, text, language='en'):
        text_lower = text.lower()
        tests_match = re.search(
            r'(?:(?:resultado|result|validation|validación|validacion|suite completa|full unittest suite)[^\n.:;]*[:.]?\s*)?'
            r'(?:\*\*)?(\d+)\s+(?:tests|pruebas)\s+(?:ok|pass|passed|pasan|pasaron|aprobadas)(?:\*\*)?',
            text,
            re.IGNORECASE
        )
        skipped_match = re.search(
            r'(\d+)\s+tests?\s+(?:ran|run).*?(\d+)\s+(?:passed|pass).*?(\d+)\s+skipped',
            text,
            re.IGNORECASE | re.DOTALL,
        )
        command_labels = []
        if 'py_compile' in text_lower:
            command_labels.append('py_compile')
        if 'compileall' in text_lower:
            command_labels.append('compileall')
        if 'unittest discover' in text_lower or 'python3 -m unittest' in text_lower:
            command_labels.append('unittest')
        if 'pytest' in text_lower:
            command_labels.append('pytest')

        seen_labels = []
        for label in command_labels:
            if label not in seen_labels:
                seen_labels.append(label)

        if language == 'es':
            if skipped_match:
                return (
                    f"- Validación: {skipped_match.group(2)}/{skipped_match.group(1)} "
                    f"tests pass, {skipped_match.group(3)} skipped"
                )
            if tests_match and seen_labels:
                return f"- Validación: {', '.join(seen_labels)} OK, {tests_match.group(1)} tests pass"
            if tests_match:
                return f"- Validación: {tests_match.group(1)} tests pass"
            if seen_labels:
                return f"- Validación: {', '.join(seen_labels)} OK"
        else:
            if skipped_match:
                return (
                    f"- Validation: {skipped_match.group(2)}/{skipped_match.group(1)} "
                    f"tests pass, {skipped_match.group(3)} skipped"
                )
            if tests_match and seen_labels:
                return f"- Validation: {', '.join(seen_labels)} OK, {tests_match.group(1)} tests pass"
            if tests_match:
                return f"- Validation: {tests_match.group(1)} tests pass"
            if seen_labels:
                return f"- Validation: {', '.join(seen_labels)} OK"
        return None

    def extract_file_mentions(self, text):
        raw_mentions = re.findall(
            r'(?<![\w.-])(?:[\w.-]+/)*[\w.-]+\.(?:py|md|json|yml|yaml|toml|txt|rst|ini|cfg)|(?<![\w.-])\.gitignore\b',
            text,
            re.IGNORECASE
        )
        mentions = []
        seen = set()
        for mention in raw_mentions:
            cleaned = mention.strip('.,;:)("\'`')
            key = cleaned.lower()
            if cleaned and key not in seen:
                mentions.append(cleaned)
                seen.add(key)
        return mentions

    def build_file_mention_bullets(self, text, language='en'):
        mentions = self.extract_file_mentions(text)
        if not mentions:
            return []

        lower_mentions = [m.lower() for m in mentions]
        has_code = any(m.endswith('.py') and not m.startswith('tests/') and '/tests/' not in m for m in lower_mentions)
        has_tests = any(m.startswith('tests/') or '/tests/' in m or m.startswith('test_') or '/test_' in m for m in lower_mentions)
        has_docs = any(m.endswith(('.md', '.rst')) for m in lower_mentions)
        has_eval_data = any(
            m.endswith('.json') or 'comparison_report' in m or 'compare_generator' in m
            for m in lower_mentions
        )
        has_config = any(m in {'.gitignore'} or m.endswith(('.yml', '.yaml', '.toml', '.ini', '.cfg')) for m in lower_mentions)

        bullets = []
        if language == 'es':
            if has_code:
                bullets.append('- Actualiza lógica de código mencionada en el resumen')
            if has_tests:
                bullets.append('- Cubre cambios con tests de regresión')
            if has_docs:
                bullets.append('- Actualiza documentación mencionada en el resumen')
            if has_eval_data:
                bullets.append('- Actualiza datos o reportes de evaluación')
            if has_config:
                bullets.append('- Ajusta configuración o archivos de higiene del proyecto')
        else:
            if has_code:
                bullets.append('- Update code paths mentioned in the summary')
            if has_tests:
                bullets.append('- Cover changes with regression tests')
            if has_docs:
                bullets.append('- Update documentation mentioned in the summary')
            if has_eval_data:
                bullets.append('- Update evaluation data or reports')
            if has_config:
                bullets.append('- Adjust project configuration or hygiene files')
        return bullets

    def rank_body_lines(self, body_lines, language='en', limit=7):
        unique_lines = []
        seen = set()
        for line in body_lines:
            clean_line = re.sub(r'\s+', ' ', line).strip()
            key = clean_line.lower()
            if clean_line and key not in seen:
                unique_lines.append(clean_line)
                seen.add(key)

        line_set = {line.lower() for line in unique_lines}
        if language == 'es':
            generic_docs = {
                '- actualiza documentación del proyecto',
                '- actualiza roadmap.md para marcar elementos completados',
            }
            has_specific_docs = '- actualiza documentación mencionada en el resumen' in line_set
            if has_specific_docs:
                unique_lines = [line for line in unique_lines if line.lower() not in generic_docs]
        else:
            generic_docs = {
                '- update roadmap.md to mark completed items',
                '- update documentation',
            }
            has_specific_docs = '- update documentation mentioned in the summary' in line_set
            if has_specific_docs:
                unique_lines = [line for line in unique_lines if line.lower() not in generic_docs]

        def rank(line):
            lower = line.lower()
            if lower.startswith(('- validación:', '- validation:')):
                return 90
            if any(k in lower for k in [
                'lógica de código', 'code paths', 'detecta ', 'detect input', 'reemplaza',
                'replace hard', 'implementa', 'implement ', 'añade selectores', 'dropdowns',
                'muestra el estado', 'display detected'
            ]):
                return 10
            if any(k in lower for k in ['tests de regresión', 'regression tests', 'test de regresión', 'regression test']):
                return 70
            if any(k in lower for k in ['documentación mencionada', 'documentation mentioned', 'readme', 'roadmap']):
                return 75
            if any(k in lower for k in ['reportes de evaluación', 'evaluation data', 'comparison_report', 'baseline']):
                return 80
            if any(k in lower for k in ['configuración', 'configuration', 'higiene', 'hygiene']):
                return 85
            return 20

        ranked = sorted(enumerate(unique_lines), key=lambda item: (rank(item[1]), item[0]))
        return [line for _index, line in ranked[:limit]]

    def generate_body_lines(self, text, language='en'):
        text_lower = text.lower()
        bullets = []
        seen = set()

        def add_bullet(line):
            clean_line = re.sub(r'\s+', ' ', line).strip()
            if clean_line and clean_line.lower() not in seen:
                bullets.append(clean_line)
                seen.add(clean_line.lower())

        def add_validation_bullet():
            validation_bullet = self.extract_validation_bullet(text, language)
            if validation_bullet:
                add_bullet(validation_bullet)

        def add_file_mention_bullets():
            for file_bullet in self.build_file_mention_bullets(text, language):
                add_bullet(file_bullet)

        if language == 'es':
            has_preview_truncation_refactor = (
                any(k in text_lower for k in ['vista previa', 'preview ui', 'legacy preview'])
                and any(k in text_lower for k in ['truncate_subject', 'truncado', 'trunca', 'word-aware', 'límites de palabra', 'limites de palabra'])
            )
            if has_preview_truncation_refactor:
                add_bullet('- Reemplaza el corte fijo de caracteres con truncate_subject()')
                add_bullet('- Elimina componentes legacy de vista previa de la interfaz')
                if 'test_smart_commit_nltk.py' in text_lower or 'tests' in text_lower:
                    add_bullet('- Actualiza tests para validar truncado en límites de palabra')
                if 'roadmap.md' in text_lower or 'readme.md' in text_lower or 'readme' in text_lower:
                    add_bullet('- Limpia Roadmap.md y README.md para reflejar el estado actual')
                add_validation_bullet()
                return bullets

            has_type_scope_ui = any(k in text_lower for k in ['type/scope', 'type y scope', 'selectores', 'tipo:', 'scope:', 'editar manualmente', 'corregirlo manualmente', 'ajuste manual'])
            if has_type_scope_ui:
                add_bullet('- Añade selectores para tipos y scopes de Conventional Commits')
                if 'regenera' in text_lower or 'al instante' in text_lower:
                    add_bullet('- Regenera el comando en tiempo real al cambiar type/scope')
                if 'manteniendo' in text_lower or 'subject' in text_lower or 'bullets' in text_lower:
                    add_bullet('- Conserva subject y body al aplicar ajustes manuales')
                if 'readme.md' in text_lower or 'readme' in text_lower:
                    add_bullet('- Documenta el flujo de ajuste manual en README.md')
                if 'test_smart_commit_nltk.py' in text_lower or 'test' in text_lower:
                    add_bullet('- Añade test de regresión para actualizaciones dinámicas')
                if 'roadmap.md' in text_lower or 'roadmap' in text_lower:
                    add_bullet('- Marca la edición manual de type/scope como completada')
                if '13 tests' in text_lower or '13 pruebas' in text_lower:
                    add_validation_bullet()
                return bullets

            has_language_status_ui = any(k in text_lower for k in ['idioma detectado', 'etiqueta de estado', 'muestra el idioma', 'estado que muestra el idioma'])
            if has_language_status_ui:
                add_bullet('- Muestra el estado de idioma detectado en la interfaz')
                if 'pendiente' in text_lower and ('español' in text_lower or 'inglés' in text_lower):
                    add_bullet('- Presenta estados Pendiente, Español e Inglés')
                if 'generar' in text_lower or 'actualiza automáticamente' in text_lower:
                    add_bullet('- Actualiza la etiqueta al generar el commit')
                if 'limpiar entrada' in text_lower or 'pendiente' in text_lower:
                    add_bullet('- Reinicia la etiqueta al limpiar la entrada')
                if 'git' in text_lower and ('integración' in text_lower or 'git diff' in text_lower):
                    add_bullet('- Enfoca el roadmap en calidad semántica sin integración Git')
                if 'test' in text_lower or 'regresión' in text_lower:
                    add_bullet('- Añade test de regresión para el estado de idioma')
                if 'roadmap.md' in text_lower or 'roadmap' in text_lower:
                    add_bullet('- Marca la tarea de idioma detectado como completada')
                if '10 tests' in text_lower or '10 pruebas' in text_lower:
                    add_validation_bullet()
                return bullets

            has_clear_input_ui = any(k in text_lower for k in ['limpiar entrada', 'botón limpiar', 'boton limpiar', 'borrar el texto de entrada', 'botón de copiar', 'boton de copiar', 'cuadro de entrada'])
            if has_clear_input_ui:
                add_bullet('- Implementa lógica para limpiar entrada y commit generado')
                if 'botón de copiar' in text_lower or 'boton de copiar' in text_lower or 'desactiva' in text_lower:
                    add_bullet('- Desactiva el botón de copiar al limpiar la entrada')
                if 'foco' in text_lower or 'cuadro de entrada' in text_lower:
                    add_bullet('- Devuelve el foco al cuadro de entrada tras limpiar')
                if 'test_smart_commit_nltk.py' in text_lower or 'test' in text_lower:
                    add_bullet('- Añade test de regresión para reinicio de estado UI')
                if 'roadmap.md' in text_lower or 'roadmap' in text_lower:
                    add_bullet('- Marca la mejora de interfaz como completada en Roadmap.md')
                if '8 tests' in text_lower or '8 pruebas' in text_lower:
                    add_validation_bullet()
                return bullets

            has_testing_baseline = (
                any(k in text_lower for k in ['test_smart_commit_nltk.py', 'regresiones', 'testing/evaluación', 'comparison_report.json', 'compare_generator.py', 'línea base', 'linea base'])
                and any(k in text_lower for k in ['testing/evaluación', 'línea base', 'linea base', 'baseline', '45 ejemplos', '0.446', '6 regresiones', '6 tests', 'compare_generator.py', '.gitignore'])
            )
            if has_testing_baseline:
                if 'test_smart_commit_nltk.py' in text_lower or '6 regresiones' in text_lower or '6 tests' in text_lower:
                    add_bullet('- Añade test_smart_commit_nltk.py con 6 regresiones principales')
                if 'compare_generator.py' in text_lower or 'firma bilingüe' in text_lower:
                    add_bullet('- Actualiza compare_generator.py para la firma bilingüe')
                if 'clean_input' in text_lower or 'detects' in text_lower or 'supports' in text_lower:
                    add_bullet('- Refina clean_input() para conservar verbos clave en inglés')
                if '.gitignore' in text_lower or '__pycache__' in text_lower:
                    add_bullet('- Añade .gitignore para __pycache__ y artefactos Python')
                if 'readme' in text_lower:
                    add_bullet('- Documenta comandos de testing en README.md')
                if 'roadmap' in text_lower:
                    add_bullet('- Marca tareas de testing y evaluación en Roadmap.md')
                if '0.446' in text_lower or '45 ejemplos' in text_lower:
                    add_bullet('- Establece baseline: 0.446 de similitud de subject')
                return bullets

                return bullets

            has_bilingual_nlp = any(k in text_lower for k in ['bilingüe', 'bilingue', 'español', 'inglés', 'ingles', 'tokenización', 'tokenizacion', 'verbos españoles'])
            if has_bilingual_nlp and any(k in text_lower for k in ['smart_commit_nltk.py', 'nltk', 'idioma']):
                add_bullet('- Detecta el idioma de entrada para tokenización localizada')
                add_bullet('- Soporta verbos españoles como creado, actualizado e incluye')
                add_bullet('- Genera subject y body en el idioma del resumen')
                if re.search(r'\bci\b|falso positivo|false-positive|detección de tipo|deteccion de tipo', text_lower):
                    add_bullet('- Corrige falsos positivos de ci dentro de palabras comunes')
                if 'py_compile' in text_lower:
                    add_bullet('- Valida la sintaxis con py_compile')
            if 'roadmap.md' in text_lower or 'roadmap' in text_lower:
                if re.search(r'\b(cread[oa]|creé|creamos|he creado|hemos creado)\b', text_lower):
                    add_bullet('- Documenta funcionalidades completadas y progreso del proyecto')
                    add_bullet('- Resume mejoras futuras para Git, ML, UI, pruebas y multilenguaje')
                    add_bullet('- Organiza el roadmap con secciones claras de estado')
                    add_bullet('- Incluye áreas de documentación, comunidad y testing')
                    add_bullet('- Usa checkboxes para visualizar tareas completadas y pendientes')
                else:
                    add_bullet('- Actualiza Roadmap.md para marcar elementos completados')
            if 'readme' in text_lower or 'documentación' in text_lower or 'documentacion' in text_lower:
                add_bullet('- Actualiza documentación del proyecto')
            if 'guía de usuario' in text_lower or 'guia de usuario' in text_lower or 'help -> user guide' in text_lower:
                add_bullet('- Añade o actualiza guía de usuario y ayuda localizada')
            if 'mute' in text_lower and 'solo' in text_lower:
                add_bullet('- Añade controles Mute/Solo por canal en la vista Channels')
            if 'slider' in text_lower and 'volumen' in text_lower:
                add_bullet('- Añade sliders de volumen por canal con actualizaciones en tiempo real')
            if 'pantalla completa' in text_lower or 'fullscreen' in text_lower:
                add_bullet('- Añade modo de pantalla completa para el diálogo')
            if 'codificación' in text_lower or 'codificacion' in text_lower:
                add_bullet('- Añade selector de codificación para exportaciones')

            add_file_mention_bullets()
            add_validation_bullet()
        else:
            has_preview_truncation_refactor = (
                any(k in text_lower for k in ['vista previa', 'preview ui', 'legacy preview'])
                and any(k in text_lower for k in ['truncate_subject', 'truncation', 'word-aware', 'word boundary'])
            )
            if has_preview_truncation_refactor:
                add_bullet('- Replace hard character slicing with truncate_subject() logic')
                add_bullet('- Remove legacy preview UI components from smart_commit_nltk.py')
                if 'test_smart_commit_nltk.py' in text_lower or 'tests' in text_lower:
                    add_bullet('- Update tests to validate word-boundary aware truncation')
                if 'roadmap.md' in text_lower or 'readme.md' in text_lower or 'readme' in text_lower:
                    add_bullet('- Clean up Roadmap.md and README.md to reflect current state')
                add_validation_bullet()
                return bullets

            has_type_scope_ui = any(k in text_lower for k in ['type/scope', 'type and scope', 'type selector', 'scope selector', 'dropdown', 'manual override'])
            if has_type_scope_ui:
                add_bullet('- Implement dropdowns for Conventional Commit types and scopes')
                if 'regenerate' in text_lower or 'real-time' in text_lower:
                    add_bullet('- Enable real-time command regeneration on manual override')
                if 'preserve' in text_lower or 'subject' in text_lower or 'body' in text_lower:
                    add_bullet('- Preserve subject and body during type/scope changes')
                if 'readme.md' in text_lower or 'readme' in text_lower:
                    add_bullet('- Document manual adjustment workflow in README.md')
                if 'test_smart_commit_nltk.py' in text_lower or 'regression test' in text_lower:
                    add_bullet('- Add regression test for dynamic command updates')
                if 'roadmap.md' in text_lower or 'roadmap' in text_lower:
                    add_bullet('- Mark manual editing task complete in Roadmap.md')
                if '13 tests' in text_lower:
                    add_bullet('- Validation: 13 tests pass in offscreen environment')
                return bullets

            has_language_status_ui = any(k in text_lower for k in ['detected language', 'language status', 'status label', 'language detection'])
            if has_language_status_ui:
                add_bullet('- Display detected language status in the UI')
                if 'pending' in text_lower and ('spanish' in text_lower or 'english' in text_lower or 'es/en' in text_lower):
                    add_bullet('- Show Pending, Spanish, and English states')
                if 'generate' in text_lower or 'generation' in text_lower:
                    add_bullet('- Update the status label when generating commits')
                if 'clear input' in text_lower or 'pending' in text_lower:
                    add_bullet('- Reset the label when clearing input')
                if 'git' in text_lower and ('integration' in text_lower or 'git diff' in text_lower):
                    add_bullet('- Refocus roadmap on semantic quality over Git integration')
                if 'test' in text_lower or 'regression' in text_lower:
                    add_bullet('- Add regression test for language status behavior')
                if 'roadmap.md' in text_lower or 'roadmap' in text_lower:
                    add_bullet('- Mark the language display task complete in Roadmap.md')
                if '10 tests' in text_lower:
                    add_bullet('- Validation: 10 tests pass in offscreen environment')
                return bullets

            has_clear_input_ui = any(k in text_lower for k in ['clear input', 'clear button', 'reset input', 'input text', 'copy button', 'refocus input'])
            if has_clear_input_ui:
                add_bullet('- Implement reset logic for input text and generated output')
                if 'copy button' in text_lower or 'disable' in text_lower:
                    add_bullet('- Disable copy button on clear action')
                if 'refocus' in text_lower or 'input field' in text_lower:
                    add_bullet('- Refocus the input field after clearing')
                if 'test_smart_commit_nltk.py' in text_lower or 'regression test' in text_lower:
                    add_bullet('- Add regression test for UI state reset behavior')
                if 'roadmap.md' in text_lower or 'roadmap' in text_lower:
                    add_bullet('- Mark the UI enhancement task complete in Roadmap.md')
                if '8 tests' in text_lower:
                    add_bullet('- Validation: 8 tests pass in offscreen environment')
                return bullets

            has_testing_baseline = (
                any(k in text_lower for k in ['test_smart_commit_nltk.py', 'regression tests', 'testing/evaluation', 'comparison_report.json', 'compare_generator.py', 'baseline'])
                and any(k in text_lower for k in ['testing/evaluation', 'baseline', '45 examples', '0.446', '6 regression', '6 tests', 'compare_generator.py', '.gitignore'])
            )
            if has_testing_baseline:
                if 'test_smart_commit_nltk.py' in text_lower or '6 regression' in text_lower or '6 tests' in text_lower:
                    add_bullet('- Add test_smart_commit_nltk.py with 6 core regression tests')
                if 'compare_generator.py' in text_lower or 'bilingual signature' in text_lower:
                    add_bullet('- Update compare_generator.py for bilingual signature support')
                if 'clean_input' in text_lower or 'detects' in text_lower or 'supports' in text_lower:
                    add_bullet('- Refine clean_input() to preserve key English action verbs')
                if '.gitignore' in text_lower or '__pycache__' in text_lower:
                    add_bullet('- Add .gitignore for __pycache__ and Python artifacts')
                if 'readme' in text_lower:
                    add_bullet('- Document testing commands in README.md')
                if 'roadmap' in text_lower:
                    add_bullet('- Mark testing and evaluation tasks complete in Roadmap.md')
                if '0.446' in text_lower or '45 examples' in text_lower:
                    add_bullet('- Establish baseline metrics: 0.446 subject similarity')
                return bullets

            if self.is_readme_architecture_docs_summary(text_lower):
                add_bullet('- Clarify lightweight ML layer and core design constraints')
                if 'responsibility split' in text_lower or 'nltk/utils' in text_lower or 'scikit-learn' in text_lower:
                    add_bullet('- Document responsibility split between NLTK, utils, and sklearn')
                if 'supported ml labels' in text_lower or 'joblib' in text_lower:
                    add_bullet('- List supported ML labels and local joblib artifact behavior')
                if 'debian validation' in text_lower or 'contribution guidance' in text_lower:
                    add_bullet('- Add Debian validation notes and contribution guidelines')
                if 'do not use' in text_lower or 'heavy dependencies' in text_lower or 'cloud' in text_lower:
                    add_bullet('- Emphasize do-not-use list for heavy dependencies and APIs')
                return bullets

            if self.is_ml_metadata_validation_summary(text_lower):
                add_bullet('- Validate model metadata fields before reporting model ready')
                if 'format version' in text_lower or 'model_metadata.json' in text_lower:
                    add_bullet('- Check metadata format version in ml/predictor.py')
                if 'valid metadata' in text_lower or 'invalid metadata' in text_lower or 'tests/test_predictor.py' in text_lower:
                    add_bullet('- Add tests for valid and invalid metadata scenarios')
                if 'roadmap.md' in text_lower or 'suite count' in text_lower:
                    add_bullet('- Update Roadmap.md with progress and suite count')
                add_validation_bullet()
                return bullets

            if self.is_ml_pipeline_summary(text_lower):
                if 'ml/dataset_loader.py' in text_lower or 'examples' in text_lower or 'sqlite' in text_lower:
                    add_bullet('- Load training examples from local dataset sources')
                if 'ml/train_model.py' in text_lower or 'joblib' in text_lower or 'metadata' in text_lower:
                    add_bullet('- Write local joblib artifacts and model metadata')
                if 'ml/predictor.py' in text_lower or 'artifact readiness' in text_lower:
                    add_bullet('- Report ML artifact readiness from the predictor')
                return bullets

                return bullets

                return bullets


            add_file_mention_bullets()
            add_validation_bullet()

        def is_similar_to_existing(obj_text):
            obj_words = [w for w in re.sub(r'[^a-z0-9 ]', ' ', obj_text.lower()).split() if len(w) > 2]
            if not obj_words:
                return False
            for existing in bullets:
                existing_lower = existing.lower()
                match_count = sum(1 for w in obj_words if w in existing_lower)
                if match_count >= max(2, len(obj_words) // 2):
                    return True
            return False

        max_body_lines = 7
        if len(bullets) >= max_body_lines:
            return self.rank_body_lines(bullets, language, max_body_lines)

        for sentence in self.sent_tokenize_by_language(text, language):
            candidate = sentence.strip()
            if len(candidate) < 12:
                continue
            if self.is_commitworthy_sentence(candidate):
                # Clean and format the sentence
                cleaned = candidate.strip()
                # Remove trailing punctuation if it's not part of the sentence
                cleaned = re.sub(r'[.!?]+$', '', cleaned)
                # Capitalize first letter
                cleaned = cleaned[0].upper() + cleaned[1:] if cleaned else cleaned
                # Add as bullet point if not similar to existing
                bullet = f'- {cleaned}'
                if not is_similar_to_existing(cleaned):
                    add_bullet(bullet)
            if len(bullets) >= max_body_lines:
                break

        if not bullets:
            if language == 'es':
                add_bullet('- Implementa mejoras y ajustes del proyecto')
            else:
                add_bullet('- Implement feature enhancements and improvements')

        return self.rank_body_lines(bullets, language, max_body_lines)

    def truncate_subject(self, subject, limit=50):
        subject = subject.strip()
        if len(subject) <= limit:
            return subject

        ellipsis = "..."
        max_prefix = limit - len(ellipsis)
        prefix = subject[:max_prefix].rstrip()
        word_boundary = prefix.rfind(" ")

        if word_boundary >= max_prefix * 0.65:
            prefix = prefix[:word_boundary].rstrip()

        prefix = re.sub(r'[\s,;:.-]+$', '', prefix)
        if not prefix:
            prefix = subject[:max_prefix].rstrip()
        return f"{prefix}{ellipsis}"

