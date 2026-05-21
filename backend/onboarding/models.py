from django.db import models
from django.conf import settings
from accounts.models import User
from django.utils import timezone


class OnboardingForm(models.Model):

    class Status(models.TextChoices):
        DRAFT    = 'draft',    'Rascunho'
        COMPLETE = 'complete', 'Concluído'
        SYNCED   = 'synced',   'Sincronizado'

    class ModeloVenda(models.TextChoices):
        HONORARIO   = 'honorario',   'Honorário fixo'
        EXITO       = 'exito',       'Êxito (% do resultado)'
        ENTRADA     = 'entrada',     'Entrada + parcelas'
        MENSALIDADE = 'mensalidade', 'Mensalidade recorrente'
        PACOTE      = 'pacote',      'Pacote único'
        HIBRIDO     = 'hibrido',     'Híbrido (fixo + êxito)'

    # ── Meta ──────────────────────────────────────────────────
    pipedrive_deal_id   = models.CharField(max_length=50, null=True, blank=True, unique=True)
    pipedrive_deal_name = models.CharField(max_length=255)
    assessor            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='onboardings')
    status              = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    # ── Step 1 — Dados do negócio ─────────────────────────────
    nome_empresa   = models.CharField(max_length=255, blank=True, default='')
    nicho          = models.CharField(max_length=255, blank=True, default='')
    produto        = models.TextField(blank=True, default='')
    tipo_venda     = models.TextField(blank=True, default='')
    ticket         = models.CharField(max_length=100, blank=True, default='')
    modelo_venda   = models.CharField(max_length=100, blank=True, default='',
                                      choices=ModeloVenda.choices)
    como_vende     = models.TextField(blank=True, default='')
    crosssell      = models.TextField(blank=True, default='')
    vendas_atual   = models.CharField(max_length=50, blank=True, default='')
    vendas_meta    = models.CharField(max_length=50, blank=True, default='')
    fat_atual      = models.CharField(max_length=100, blank=True, default='')
    fat_meta       = models.CharField(max_length=100, blank=True, default='')
    volume_leads   = models.CharField(max_length=255, blank=True, default='')
    funcionarios   = models.CharField(max_length=255, blank=True, default='')
    # Infraestrutura
    entrada_crm           = models.CharField(max_length=255, blank=True, default='')
    integracoes           = models.CharField(max_length=255, blank=True, default='')
    followup_estruturado  = models.CharField(max_length=50, blank=True, default='')
    gravacoes             = models.CharField(max_length=50, blank=True, default='')

    # ── Step 2 — Lead ─────────────────────────────────────────
    perfil_lead      = models.TextField(blank=True, default='')
    dor_principal    = models.TextField(blank=True, default='')
    objecoes         = models.TextField(blank=True, default='')
    tom              = models.JSONField(default=list)   # lista (multi-select)
    caso_sucesso     = models.TextField(blank=True, default='')
    gatilho_urgencia = models.TextField(blank=True, default='')

    # ── Step 3 — Funis ────────────────────────────────────────
    # funis: lista dos slugs ativos ['trafego','prospeccao',...]
    funis            = models.JSONField(default=list)
    # etapas de cada funil: [{name, action, active, optional?}, ...]
    trafego_etapas   = models.JSONField(default=list)
    trafego_isca     = models.CharField(max_length=255, blank=True, default='')
    trafego_plataforma = models.CharField(max_length=255, blank=True, default='')
    trafego_dias     = models.CharField(max_length=20, blank=True, default='')
    trafego_bot      = models.TextField(blank=True, default='')
    prosp_etapas     = models.JSONField(default=list)
    prosp_perfil     = models.CharField(max_length=255, blank=True, default='')
    prosp_dias       = models.CharField(max_length=20, blank=True, default='')
    prosp_canais     = models.JSONField(default=list)
    prosp_fonte      = models.CharField(max_length=255, blank=True, default='')
    social_etapas    = models.JSONField(default=list)
    social_plat      = models.CharField(max_length=50, blank=True, default='')
    social_dias      = models.CharField(max_length=20, blank=True, default='')
    carteira_etapas  = models.JSONField(default=list)
    carteira_quem    = models.CharField(max_length=255, blank=True, default='')
    cart_freq        = models.CharField(max_length=50, blank=True, default='')
    posvenda_etapas  = models.JSONField(default=list)
    posvenda_obs     = models.TextField(blank=True, default='')
    custom_etapas    = models.JSONField(default=list)
    custom_fluxo     = models.TextField(blank=True, default='')

    # ── Step 4 — Time ─────────────────────────────────────────
    sdr               = models.CharField(max_length=255, blank=True, default='')
    closer            = models.CharField(max_length=255, blank=True, default='')
    especialista      = models.CharField(max_length=255, blank=True, default='')
    empresa_scripts   = models.CharField(max_length=255, blank=True, default='')
    perfil_operador   = models.TextField(blank=True, default='')
    etapas_fechamento = models.JSONField(default=list)  # [{num, text, active}, ...]
    fech_especifico   = models.TextField(blank=True, default='')
    tipo_reuniao      = models.TextField(blank=True, default='')
    passagem          = models.TextField(blank=True, default='')
    apresenta_preco   = models.TextField(blank=True, default='')
    metodo            = models.JSONField(default=list)
    condicao_especial = models.TextField(blank=True, default='')
    objecoes_fecha    = models.TextField(blank=True, default='')

    # ── Step 5 — Scripts ──────────────────────────────────────
    wpp_perguntas    = models.TextField(blank=True, default='')
    wpp_criterio     = models.CharField(max_length=255, blank=True, default='')
    wpp_desqualifica = models.CharField(max_length=255, blank=True, default='')
    wpp_proximo      = models.CharField(max_length=100, blank=True, default='')
    lig_pitch        = models.TextField(blank=True, default='')
    lig_perguntas    = models.TextField(blank=True, default='')
    lig_objecoes     = models.TextField(blank=True, default='')
    fech_estrutura   = models.TextField(blank=True, default='')
    particularidades = models.TextField(blank=True, default='')
    tem_ref          = models.CharField(max_length=100, blank=True, default='')
    ref_cliente      = models.CharField(max_length=255, blank=True, default='')

    # ── Step 6 — Datas ────────────────────────────────────────
    plano_selecionado = models.CharField(max_length=100, blank=True, default='')
    assessorias       = models.JSONField(default=list)  # [{date, time, responsible}, ...]
    cs_encontros      = models.JSONField(default=list)
    bonus_encontros   = models.JSONField(default=list)  # [{label, date, time, responsible}, ...]

    # ── Step 7 — Pesquisa ─────────────────────────────────────
    fonte_conteudo        = models.CharField(max_length=100, blank=True, default='')
    como_descobriu        = models.TextField(blank=True, default='')
    decisivo_prospeccao   = models.JSONField(default=list)
    experiencia_reuniao   = models.JSONField(default=list)
    indicador_sucesso     = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.pipedrive_deal_name} ({self.get_status_display()})'


class GeneratedMaterial(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        RUNNING = 'running'
        COMPLETE = 'complete'
        FAILED = 'failed'

    onboarding = models.OneToOneField(OnboardingForm, on_delete=models.CASCADE, related_name='material')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    crm = models.JSONField(null=True, blank=True)
    closing = models.JSONField(null=True, blank=True)
    qualification = models.JSONField(null=True, blank=True)
    quality_alerts = models.JSONField(default=list)
    error = models.TextField(blank=True)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MaterialShare(models.Model):
    material = models.OneToOneField(GeneratedMaterial, on_delete=models.CASCADE, related_name='share')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    password_hash = models.CharField(max_length=255, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_active(self):
        if self.revoked:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
    
    def __str__(self):
        return f'Share {self.token[:8]}... -> material {self.material_id}'

class OnboardingRule(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='created_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.name
    
class OnboardingRuleAck(models.Model):
    rule = models.ForeignKey(OnboardingRule, on_delete=models.CASCADE, related_name='acks')
    onboarding = models.ForeignKey(OnboardingForm, on_delete=models.CASCADE, related_name='rule_acks')
    checked_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rule', 'onboarding')


