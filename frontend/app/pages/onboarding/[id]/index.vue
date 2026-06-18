<template>
  <div class="min-h-full">
    <!-- Top bar -->
    <div class="sticky top-0 z-20 bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-white/[0.06]">
      <div class="max-w-3xl mx-auto px-6 py-3 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0">
          <NuxtLink to="/onboarding" class="text-white/30 hover:text-white/60 transition-colors shrink-0">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
            </svg>
          </NuxtLink>
          <div class="min-w-0">
            <p class="text-white text-sm font-medium truncate">{{ dealName || 'Onboarding' }}</p>
            <p v-if="status !== 'draft'" class="text-xs" :class="status === 'synced' ? 'text-emerald-400' : 'text-blue-300'">
              {{ STATUS_LABEL[status] }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-3 shrink-0">
          <button
            v-if="materials?.status === 'complete'"
            class="px-3 py-1.5 text-xs font-semibold bg-white text-neutral-900 rounded-full hover:-translate-y-0.5 transition-all flex items-center gap-1.5"
            @click="openMaterials"
          >
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
            Materiais
          </button>
          <span class="text-xs text-white/30">{{ step }}/8</span>
          <div v-if="saving" class="flex items-center gap-1.5 text-xs text-white/30">
            <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            Salvando...
          </div>
        </div>
      </div>

      <!-- Progress + step nav -->
      <div class="h-0.5 bg-white/[0.04]">
        <div class="h-full bg-white/30 transition-all duration-300" :style="{ width: `${(step / 8) * 100}%` }" />
      </div>
      <div class="max-w-3xl mx-auto px-6 py-2 flex gap-1 overflow-x-auto scrollbar-hide">
        <button
          v-for="(label, i) in STEP_LABELS"
          :key="i"
          class="px-3 py-1 rounded-full text-xs font-medium tracking-wide whitespace-nowrap transition-all"
          :class="step === i + 1
            ? 'bg-white/10 text-white'
            : step > i + 1
              ? 'text-white/40'
              : 'text-white/20 hover:text-white/40'"
          @click="jumpTo(i + 1)"
        >
          <span v-if="step > i + 1" class="mr-1 opacity-60">✓</span>{{ label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div v-if="loading" class="max-w-3xl mx-auto px-6 py-12 space-y-4">
      <div v-for="i in 3" :key="i" class="h-32 bg-white/[0.03] rounded-2xl animate-pulse" />
    </div>
    <div v-else class="max-w-3xl mx-auto px-6 py-8 pb-24">

      <!-- ══════ STEP 1 — NEGÓCIO ══════ -->
      <div v-show="step === 1">
        <ObStepHeader tag="Etapa 1 de 8" title="Dados do negócio" desc="Base de todos os scripts. Quanto mais específico, melhor." />

        <ObCard title="Identificação">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <ObField label="Nome da empresa" required>
              <input v-model="form.nome_empresa" placeholder="Ex: Béda Advocacia" v-bind="inputClass" />
            </ObField>
            <ObField label="Nicho ou segmento" required>
              <input v-model="form.nicho" placeholder="Ex: Direito Previdenciário" v-bind="inputClass" />
            </ObField>
          </div>
          <ObField label="O que vende ou entrega" required hint="Descreva como explicaria para o lead">
            <div class="flex items-start gap-2">
              <textarea v-model="form.produto" placeholder="Ex: Assessoria jurídica para trabalhadores com Auxílio-Doença negado pelo INSS..." v-bind="textareaClass" class="flex-1" />
              <ObMicButton v-model="form.produto" />
            </div>
          </ObField>
          <ObField label="Tipo de venda">
            <ObChips :options="['B2B — Empresa para Empresa','B2C — Empresa para Consumidor']" :value="[form.tipo_venda]" single @toggle="(v) => form.tipo_venda = form.tipo_venda === v ? '' : v" />
          </ObField>
        </ObCard>

        <ObCard title="Comercial">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <ObField label="Ticket médio" required>
              <input v-model="form.ticket" placeholder="Ex: R$ 2.500" v-bind="inputClass" />
            </ObField>
            <ObField label="Modelo de cobrança">
              <select v-model="form.modelo_venda" v-bind="inputClass" class="!appearance-none">
                <option value="">Selecione</option>
                <option>Honorário fixo</option>
                <option>Êxito (% do resultado)</option>
                <option>Entrada + parcelas</option>
                <option>Mensalidade recorrente</option>
                <option>Pacote único</option>
                <option>Híbrido (fixo + êxito)</option>
              </select>
            </ObField>
          </div>
          <ObField label="Como vende hoje" hint="Mesmo que seja informal ou sem processo definido">
            <div class="flex items-start gap-2">
              <textarea v-model="form.como_vende" placeholder="Ex: A doutora atende quem aparece, não existe prospecção..." v-bind="textareaClass" style="min-height:58px;line-height:1.6" class="flex-1" />
              <ObMicButton v-model="form.como_vende" />
            </div>
          </ObField>
          <ObField label="Cross-sell ou up-sell?">
            <input v-model="form.crosssell" placeholder="Ex: Trabalhista → Previdenciário. Ticket sobe de R$1.500 para R$3.200." v-bind="inputClass" />
          </ObField>
        </ObCard>

        <ObCard title="Métricas">
          <div class="grid grid-cols-2 gap-px bg-white/[0.06] rounded-xl overflow-hidden mb-4">
            <ObMetricCell label="Vendas/mês HOJE"><input v-model="form.vendas_atual" placeholder="0" v-bind="metricInputClass" /></ObMetricCell>
            <ObMetricCell label="Meta de vendas/mês ↑"><input v-model="form.vendas_meta" placeholder="0" v-bind="metricInputClass" /></ObMetricCell>
            <ObMetricCell label="Faturamento mensal HOJE"><input v-model="form.fat_atual" placeholder="R$ 0" v-bind="metricInputClass" /></ObMetricCell>
            <ObMetricCell label="Faturamento que quer alcançar ↑"><input v-model="form.fat_meta" placeholder="R$ 0" v-bind="metricInputClass" /></ObMetricCell>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <ObField label="Volume de leads/mês">
              <input v-model="form.volume_leads" placeholder="Ex: 80 leads por mês" v-bind="inputClass" />
            </ObField>
            <ObField label="Funcionários totais">
              <input v-model="form.funcionarios" placeholder="Ex: 4 funcionários" v-bind="inputClass" />
            </ObField>
          </div>
        </ObCard>

        <ObCard title="Infraestrutura">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <ObField label="Como os leads entram no CRM">
              <input v-model="form.entrada_crm" placeholder="Ex: WhatsApp, formulário Meta, direct" v-bind="inputClass" />
            </ObField>
            <ObField label="Integrações necessárias">
              <input v-model="form.integracoes" placeholder="Ex: API Oficial, Calendly, Chatbear" v-bind="inputClass" />
            </ObField>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <ObField label="Follow-up estruturado hoje?">
              <ObChips :options="['Sim, estruturado','Parcialmente','Não existe']" :value="[form.followup_estruturado]" single @toggle="(v) => form.followup_estruturado = form.followup_estruturado === v ? '' : v" />
            </ObField>
            <ObField label="Atendimentos gravados?">
              <ObChips :options="['Sim, tenho gravações','Não tenho']" :value="[form.gravacoes]" single @toggle="(v) => form.gravacoes = form.gravacoes === v ? '' : v" />
            </ObField>
          </div>
        </ObCard>
      </div>

      <!-- ══════ STEP 2 — LEAD ══════ -->
      <div v-show="step === 2">
        <ObStepHeader tag="Etapa 2 de 8" title="Perfil do lead" desc="Define o tom, as dores e os argumentos de todos os scripts." />

        <ObCard title="Quem é o lead">
          <ObField label="Perfil do lead ideal (ICP)" required>
            <input v-model="form.perfil_lead" placeholder="Ex: Trabalhador CLT, 30 a 60 anos, afastado por doença, INSS negado ou em análise" v-bind="inputClass" />
          </ObField>
          <ObField label="Dor principal" required hint="O que ele sente antes de entrar em contato. Quanto mais específico, melhor.">
            <div class="flex items-start gap-2">
              <textarea v-model="form.dor_principal" placeholder="Ex: Está sem renda há meses. INSS negou. Não sabe o que fazer e tem medo de perder o prazo do recurso." v-bind="textareaClass" class="flex-1" />
              <ObMicButton v-model="form.dor_principal" />
            </div>
          </ObField>
          <ObField label="Objeções mais comuns">
            <div class="flex items-start gap-2">
              <textarea v-model="form.objecoes" placeholder="Ex: Não tenho dinheiro / Vou tentar sozinho / Está caro / Preciso pensar" v-bind="textareaClass" style="min-height:58px;line-height:1.6" class="flex-1" />
              <ObMicButton v-model="form.objecoes" />
            </div>
          </ObField>
        </ObCard>

        <ObCard title="Comunicação e prova">
          <ObField label="Tom de comunicação" required>
            <ObChips :options="['Formal e técnico','Direto e objetivo','Empático e próximo','Urgência e pressão','Educativo e didático','Motivacional']" :value="form.tom" @toggle="(v) => toggleChip(form.tom, v)" />
          </ObField>
          <ObField label="Caso de sucesso para os scripts" required hint="Um resultado real e concreto.">
            <div class="flex items-start gap-2">
              <textarea v-model="form.caso_sucesso" placeholder="Ex: Cliente teve INSS negado por 8 meses. Entramos com recurso e em 4 meses ela passou a receber R$ 1.518 por mês." v-bind="textareaClass" class="flex-1" />
              <ObMicButton v-model="form.caso_sucesso" />
            </div>
          </ObField>
          <ObField label="Gatilho de urgência do nicho" required hint="O que acontece de ruim se o lead não agir agora">
            <div class="flex items-start gap-2">
              <textarea v-model="form.gatilho_urgencia" placeholder="Ex: O prazo para recurso administrativo é 30 dias após a negativa. Depois só via judicial — mais lento e mais caro." v-bind="textareaClass" style="min-height:58px;line-height:1.6" class="flex-1" />
              <ObMicButton v-model="form.gatilho_urgencia" />
            </div>
          </ObField>
        </ObCard>
      </div>

      <!-- ══════ STEP 3 — FUNIS ══════ -->
      <div v-show="step === 3">
        <ObStepHeader tag="Etapa 3 de 8" title="Funis e etapas" desc="Selecione os funis deste cliente. Cada um abre com as etapas padrão já marcadas." />

        <ObCard title="Quais funis este cliente vai ter?">
          <div class="grid grid-cols-3 gap-2">
            <ObFunilCard v-for="f in FUNIS" :key="f.key" :name="f.name" :desc="f.desc" :active="form.funis.includes(f.key)" @click="toggleFunil(f.key)" />
          </div>
        </ObCard>

        <!-- Tráfego pago -->
        <template v-if="form.funis.includes('trafego')">
          <ObFunilBloco title="Tráfego Pago — Etapas do Pipedrive" badge="Padrão">
            <ObEtapasList :etapas="form.trafego_etapas" @add="addEtapa('trafego')" @move="(i, dir) => moveInList(form.trafego_etapas, i, dir)" />
            <div class="grid grid-cols-2 gap-4 mt-4">
              <ObField label="Isca ou oferta de entrada">
                <input v-model="form.trafego_isca" placeholder="Ex: Consulta gratuita, cálculo grátis, ebook" v-bind="inputClass" />
              </ObField>
              <ObField label="Plataforma de origem">
                <input v-model="form.trafego_plataforma" placeholder="Ex: Meta Ads, Google, TikTok" v-bind="inputClass" />
              </ObField>
            </div>
            <ObField label="Dias de cadência" class="mt-4">
              <ObChips :options="['3 dias','5 dias','6 dias','7 dias']" :value="[form.trafego_dias]" single @toggle="(v) => form.trafego_dias = form.trafego_dias === v ? '' : v" />
            </ObField>
            <ObField label="Ferramenta de entrada (bot, API Oficial...)" class="mt-4">
              <textarea v-model="form.trafego_bot" placeholder="Ex: Chatbear + API Oficial. Bot faz 2 perguntas. Só cai no Pipedrive quem confirmar interesse." v-bind="textareaClass" style="min-height:52px" />
            </ObField>
          </ObFunilBloco>
        </template>

        <!-- Prospecção ativa -->
        <template v-if="form.funis.includes('prospeccao')">
          <ObFunilBloco title="Prospecção Ativa — Etapas do Pipedrive" badge="Padrão">
            <ObEtapasList :etapas="form.prosp_etapas" @add="addEtapa('prosp')" @move="(i, dir) => moveInList(form.prosp_etapas, i, dir)" />
            <div class="grid grid-cols-2 gap-4 mt-4">
              <ObField label="Perfil a prospectar">
                <input v-model="form.prosp_perfil" placeholder="Ex: Advogados trabalhistas com escritório próprio" v-bind="inputClass" />
              </ObField>
              <ObField label="Dias de cadência">
                <ObChips :options="['3 dias','5 dias','6 dias','7 dias']" :value="[form.prosp_dias]" single @toggle="(v) => form.prosp_dias = form.prosp_dias === v ? '' : v" />
              </ObField>
            </div>
            <ObField label="Canais de abordagem" class="mt-4">
              <ObChips :options="['Ligação','WhatsApp','LinkedIn','E-mail']" :value="form.prosp_canais" @toggle="(v) => toggleChip(form.prosp_canais, v)" />
            </ObField>
            <ObField label="Como o SDR encontra os leads" class="mt-4">
              <input v-model="form.prosp_fonte" placeholder="Ex: Apollo, LinkedIn, Google Maps, lista própria" v-bind="inputClass" />
            </ObField>
          </ObFunilBloco>
        </template>

        <!-- Social Selling -->
        <template v-if="form.funis.includes('social')">
          <ObFunilBloco title="Social Selling — Etapas do Pipedrive" badge="Padrão">
            <ObEtapasList :etapas="form.social_etapas" @add="addEtapa('social')" @move="(i, dir) => moveInList(form.social_etapas, i, dir)" />
            <div class="grid grid-cols-2 gap-4 mt-4">
              <ObField label="Plataforma principal">
                <ObChips :options="['Instagram','LinkedIn','Ambos']" :value="[form.social_plat]" single @toggle="(v) => form.social_plat = form.social_plat === v ? '' : v" />
              </ObField>
              <ObField label="Dias de aquecimento antes do contato">
                <ObChips :options="['3 dias','5 dias','7 dias']" :value="[form.social_dias]" single @toggle="(v) => form.social_dias = form.social_dias === v ? '' : v" />
              </ObField>
            </div>
          </ObFunilBloco>
        </template>

        <!-- Carteira / Reativação -->
        <template v-if="form.funis.includes('carteira')">
          <ObFunilBloco title="Carteira / Reativação" badge="Padrão">
            <ObEtapasList :etapas="form.carteira_etapas" @add="addEtapa('carteira')" @move="(i, dir) => moveInList(form.carteira_etapas, i, dir)" />
            <div class="grid grid-cols-2 gap-4 mt-4">
              <ObField label="Quem entra nesta carteira">
                <input v-model="form.carteira_quem" placeholder="Ex: Leads perdidos há mais de 60 dias" v-bind="inputClass" />
              </ObField>
              <ObField label="Frequência de contato">
                <ObChips :options="['Semanal','Quinzenal','Mensal']" :value="[form.cart_freq]" single @toggle="(v) => form.cart_freq = form.cart_freq === v ? '' : v" />
              </ObField>
            </div>
          </ObFunilBloco>
        </template>

        <!-- Pós-venda -->
        <template v-if="form.funis.includes('posvenda')">
          <ObFunilBloco title="Pós-venda / Indicação" badge="Altamente personalizável">
            <ObEtapasList :etapas="form.posvenda_etapas" @add="addEtapa('posvenda')" @move="(i, dir) => moveInList(form.posvenda_etapas, i, dir)" />
            <ObField label="Particularidades do pós-venda deste cliente" class="mt-4">
              <textarea v-model="form.posvenda_obs" placeholder="Ex: Tem programa de indicação estruturado com desconto de 10% para quem indica." v-bind="textareaClass" style="min-height:56px" />
            </ObField>
          </ObFunilBloco>
        </template>

        <!-- Funil customizado -->
        <template v-if="form.funis.includes('custom')">
          <ObFunilBloco title="Funil Customizado" badge="Manual">
            <ObField label="Descreva o fluxo completo de entrada do lead">
              <textarea v-model="form.custom_fluxo" placeholder="Ex: Lead vê anúncio → bot faz 3 perguntas → se qualificado, agenda via Calendly → cai no Pipedrive como reunião agendada" v-bind="textareaClass" style="min-height:64px" />
            </ObField>
            <ObEtapasList :etapas="form.custom_etapas" @add="addEtapa('custom')" @move="(i, dir) => moveInList(form.custom_etapas, i, dir)" class="mt-4" />
          </ObFunilBloco>
        </template>
      </div>

      <!-- ══════ STEP 4 — TIME ══════ -->
      <div v-show="step === 4">
        <ObStepHeader tag="Etapa 4 de 8" title="Fechamento" desc="Estrutura da reunião de fechamento. Desmarque etapas que não se aplicam e reordene conforme o fluxo do cliente." />

        <ObCard title="Estrutura da reunião de fechamento">
          <p class="text-xs text-neutral-500 mb-3">Etapas padrão já marcadas. Edite o texto, adicione ou remova etapas, desmarque o que não se aplica e use ↑/↓ para reordenar.</p>
          <div class="space-y-2">
            <div
              v-for="(etapa, i) in form.etapas_fechamento"
              :key="i"
              class="w-full flex items-center gap-3 p-3 rounded-xl border transition-all text-left"
              :class="etapa.active
                ? 'border-white/10 bg-white/[0.03]'
                : 'border-white/[0.04] bg-transparent opacity-40'"
            >
              <button
                class="w-4 h-4 rounded flex items-center justify-center shrink-0 transition-all text-xs font-black"
                :class="etapa.active ? 'bg-white text-neutral-900' : 'border border-white/20'"
                @click="etapa.active = !etapa.active"
              >
                <span v-if="etapa.active">✓</span>
              </button>
              <span class="text-xs text-white/40 font-mono shrink-0">{{ etapa.num }}</span>
              <input
                v-model="etapa.text"
                class="flex-1 bg-transparent border-none text-sm min-w-0 focus:outline-none"
                :class="etapa.active ? 'text-white/80 focus:text-white' : 'text-white/30'"
                :disabled="!etapa.active"
                placeholder="Nome da etapa..."
              />
              <div class="flex items-center gap-0.5 shrink-0">
                <button
                  class="w-6 h-6 flex items-center justify-center rounded text-sm leading-none text-white/30 hover:text-white/70 hover:bg-white/5 disabled:opacity-20 disabled:hover:bg-transparent disabled:hover:text-white/30 transition-all"
                  :disabled="i === 0"
                  title="Mover para cima"
                  @click="moveEtapaFechamento(i, -1)"
                >↑</button>
                <button
                  class="w-6 h-6 flex items-center justify-center rounded text-sm leading-none text-white/30 hover:text-white/70 hover:bg-white/5 disabled:opacity-20 disabled:hover:bg-transparent disabled:hover:text-white/30 transition-all"
                  :disabled="i === form.etapas_fechamento.length - 1"
                  title="Mover para baixo"
                  @click="moveEtapaFechamento(i, 1)"
                >↓</button>
                <button
                  class="w-6 h-6 flex items-center justify-center rounded text-base leading-none text-white/30 hover:text-red-400 hover:bg-white/5 transition-all"
                  title="Remover etapa"
                  @click="removeEtapaFechamento(i)"
                >×</button>
              </div>
            </div>
          </div>
          <button
            type="button"
            class="w-full mt-2 py-2 border border-dashed border-white/10 rounded-xl text-xs text-white/30 font-semibold tracking-widest uppercase hover:border-white/20 hover:text-white/50 transition-all"
            @click="addEtapaFechamento"
          >
            + Adicionar etapa
          </button>
        </ObCard>

        <div class="mb-4">
          <button
            type="button"
            class="w-full flex items-center justify-between gap-3 px-4 py-3 rounded-2xl bg-white/[0.03] ring-1 ring-white/[0.06] hover:bg-white/[0.05] transition-all"
            @click="showFechExtra = !showFechExtra"
          >
            <span class="flex items-center gap-2.5">
              <span class="text-sm font-medium text-white/80">Mais opções</span>
              <span class="text-[10px] uppercase tracking-widest font-semibold text-white/40 px-2 py-0.5 rounded-full bg-white/5 ring-1 ring-white/10">Opcional</span>
            </span>
            <svg class="w-4 h-4 text-white/40 transition-transform" :class="showFechExtra ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
            </svg>
          </button>
          <div v-show="showFechExtra" class="mt-4">
            <ObCard title="Fechamento — detalhes específicos">
              <ObField label="Particularidades no funil" hint="Regras/peculiaridades dos funis que a IA deve respeitar ao montar etapas e cadências.">
                <textarea v-model="form.fech_estrutura" placeholder="Ex:&#10;Funil de tráfego não usa ligação nos 2 primeiros dias.&#10;Lead de indicação pula a etapa de qualificação.&#10;Nunca mandar áudio no WhatsApp." v-bind="textareaClass" style="min-height:100px" />
              </ObField>
              <ObField label="Particularidades operacionais" hint="Regras de negócio, restrições legais, critério especial..." class="mt-4">
                <textarea v-model="form.particularidades" placeholder="Ex: Só entra no Pipedrive quem confirmar no chatbot. Leads de indicação vão direto pro closer sem cadência." v-bind="textareaClass" style="min-height:58px" />
              </ObField>
            </ObCard>

            <ObCard title="Referência de material existente">
              <ObField label="Já existe algum material que a IA pode tomar como referência?" hint="Se sim, indique o cliente.">
                <ObChips :options="['Sim, tenho','Não tenho']" :value="[form.tem_ref]" single @toggle="(v) => form.tem_ref = form.tem_ref === v ? '' : v" />
              </ObField>
              <div v-if="form.tem_ref === 'Sim, tenho'" class="mt-4">
                <ObField label="De qual cliente?">
                  <input v-model="form.ref_cliente" placeholder="Ex: Béda Advocacia, CBC Contabilidade..." v-bind="inputClass" />
                </ObField>
              </div>
            </ObCard>
          </div>
        </div>
      </div>

      <!-- ══════ STEP 5 — SCRIPTS ══════ -->
      <div v-show="step === 5">
        <div class="flex items-start justify-between gap-4">
          <ObStepHeader tag="Etapa 5 de 8" title="Scripts avançados" desc="Só preencha o que é específico deste cliente. O que for padrão já está no sistema." class="min-w-0" />
          <button
            class="shrink-0 mt-1 w-8 h-8 flex items-center justify-center rounded-full text-base hover:bg-white/10 transition-all disabled:opacity-40"
            :disabled="suggestingScripts"
            title="Preencher campos com IA baseado nas respostas anteriores (GPTCBA)"
            @click="suggestScripts"
          >
            <svg v-if="suggestingScripts" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <span v-else>✨</span>
          </button>
        </div>

        <ObCard title="Qualificação — WhatsApp">
          <ObField label="Perguntas de qualificação via WhatsApp" required hint="Liste na ordem. A IA transforma em mensagens naturais de conversa.">
            <div class="flex items-start gap-2">
              <textarea v-model="form.wpp_perguntas" placeholder="1. Você ainda trabalha na empresa ou já foi demitido?&#10;2. Quanto tempo trabalhou lá?&#10;3. Recebia horas extras não pagas?" v-bind="textareaClass" class="flex-1" />
              <ObMicButton v-model="form.wpp_perguntas" />
            </div>
          </ObField>
          <div class="grid grid-cols-2 gap-4 mt-4">
            <ObField label="Critério mínimo para avançar">
              <input v-model="form.wpp_criterio" placeholder="Ex: Mais de 1 ano + horas extras" v-bind="inputClass" />
            </ObField>
            <ObField label="O que desqualifica na hora">
              <input v-model="form.wpp_desqualifica" placeholder="Ex: Autônomo sem carteira" v-bind="inputClass" />
            </ObField>
          </div>
          <ObField label="Próximo passo após qualificar" class="mt-4">
            <ObChips :options="['Agendar reunião','Transferir para closer','Solicitar documentos','Ligar na hora','Enviar proposta direta']" :value="[form.wpp_proximo]" single @toggle="(v) => form.wpp_proximo = form.wpp_proximo === v ? '' : v" />
          </ObField>
        </ObCard>

        <ObCard title="Qualificação — Ligação">
          <ObField label="Pitch de abertura da ligação" required hint="O que o SDR fala nos primeiros 10 segundos para não perder o lead">
            <div class="flex items-start gap-2">
              <textarea v-model="form.lig_pitch" placeholder="Ex: Alô, [nome]? Aqui é o [nome], da [empresa]. Você entrou em contato sobre [assunto], lembra? Posso fazer algumas perguntas rápidas?" v-bind="textareaClass" class="flex-1" />
              <ObMicButton v-model="form.lig_pitch" />
            </div>
          </ObField>
          <ObField label="Perguntas de qualificação na ligação" required class="mt-4">
            <div class="flex items-start gap-2">
              <textarea v-model="form.lig_perguntas" placeholder="1. Você ainda trabalha na empresa ou já foi demitido?&#10;2. Quanto tempo de empresa?&#10;3. Recebia horas extras?" v-bind="textareaClass" class="flex-1" />
              <ObMicButton v-model="form.lig_perguntas" />
            </div>
          </ObField>
          <ObField label="Objeções comuns na ligação e como tratar" class="mt-4">
            <div class="flex items-start gap-2">
              <textarea v-model="form.lig_objecoes" placeholder="Não tenho tempo → Entendo, leva 2 minutos. Posso seguir?&#10;Não tenho interesse → [prova social rápida]" v-bind="textareaClass" style="min-height:58px;line-height:1.6" class="flex-1" />
              <ObMicButton v-model="form.lig_objecoes" />
            </div>
          </ObField>
        </ObCard>
      </div>

      <!-- ══════ STEP 6 — DATAS ══════ -->
      <div v-show="step === 6">
        <ObStepHeader tag="Etapa 6 de 8" title="Datas do projeto" desc="Selecione o plano e preencha as datas combinadas." />

        <ObCard title="Plano contratado">
          <div class="grid grid-cols-4 gap-2">
            <ObFunilCard
              v-for="(cfg, key) in PLANOS"
              :key="key"
              :name="key.toUpperCase()"
              :desc="cfg.label"
              :active="form.plano_selecionado === key"
              @click="selectPlano(key)"
            />
          </div>
        </ObCard>

        <template v-if="form.plano_selecionado">
          <ObCard v-if="form.assessorias.length > 0" title="Assessorias">
            <div class="space-y-2">
              <ObDateRow
                v-for="(a, i) in form.assessorias"
                :key="i"
                :num="i + 1"
                :entry="a"
                label="Assessoria"
                responsible-label="Assessor"
              />
            </div>
          </ObCard>

          <ObCard v-if="form.cs_encontros.length > 0" title="Encontros de CS — Amanda">
            <div class="space-y-2">
              <ObDateRow
                v-for="(c, i) in form.cs_encontros"
                :key="i"
                :num="i + 1"
                :entry="c"
                label="CS"
                responsible-label="Amanda"
              />
            </div>
          </ObCard>

          <ObCard title="Encontros bônus">
            <p class="text-xs text-neutral-500 mb-3">Adicione encontros extras combinados fora do plano.</p>
            <div class="space-y-2 mb-3">
              <div
                v-for="(b, i) in form.bonus_encontros"
                :key="i"
                class="grid grid-cols-4 gap-2 items-center bg-white/[0.02] rounded-xl p-3"
              >
                <input v-model="b.label" placeholder="Label" v-bind="inputClass" class="col-span-1" />
                <input v-model="b.date" type="date" v-bind="inputClass" />
                <input v-model="b.time" type="time" v-bind="inputClass" />
                <div class="flex items-center gap-2">
                  <input v-model="b.responsible" placeholder="Responsável" v-bind="inputClass" class="flex-1" />
                  <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg" @click="form.bonus_encontros.splice(i, 1)">×</button>
                </div>
              </div>
            </div>
            <button
              class="w-full py-2.5 border border-dashed border-white/10 rounded-xl text-xs text-white/30 font-semibold tracking-widest uppercase hover:border-white/20 hover:text-white/50 transition-all"
              @click="addBonus"
            >
              + Adicionar encontro bônus
            </button>
          </ObCard>
        </template>
      </div>

      <!-- ══════ STEP 7 — PESQUISA ══════ -->
      <div v-show="step === 7">
        <ObStepHeader tag="Etapa 7 de 8" title="Pesquisa de mercado" desc="Respondida pelo cliente na reunião. Alimenta a IA com linguagem real e intenção de compra." />

        <ObCard title="Consumo de conteúdo">
          <ObField label="Quando busca conteúdo aprofundado sobre negócios, qual fonte usa?">
            <div class="space-y-2">
              <ObOptRow v-for="opt in ['Instagram','YouTube','LinkedIn','Podcasts','TikTok','Outro']" :key="opt" :text="opt" :selected="form.fonte_conteudo === opt" @click="form.fonte_conteudo = form.fonte_conteudo === opt ? '' : opt" />
            </div>
            <input v-if="form.fonte_conteudo === 'Outro'" v-model="form.fonte_conteudo_outro" placeholder="Descreva qual fonte..." v-bind="inputClass" class="mt-3" />
          </ObField>
        </ObCard>

        <ObCard title="Descoberta da marca">
          <ObField label="Como ouviu falar do Grupo Enriquecedor?">
            <div class="space-y-2">
              <ObOptRow v-for="opt in ['Um amigo ou parceiro recomendou','Vi um conteúdo ou anúncio no Instagram, LinkedIn ou YouTube','Pesquisei sobre o problema e encontrei vocês','Outro']" :key="opt" :text="opt" :selected="form.como_descobriu === opt" @click="form.como_descobriu = form.como_descobriu === opt ? '' : opt" />
            </div>
            <input v-if="form.como_descobriu === 'Outro'" v-model="form.como_descobriu_outro" placeholder="Descreva como descobriu..." v-bind="inputClass" class="mt-3" />
          </ObField>
        </ObCard>

        <ObCard title="O que foi decisivo na prospecção">
          <ObField label="O que o pré-vendedor fez que foi decisivo para você aceitar a reunião?">
            <div class="space-y-2">
              <ObOptRow
                v-for="opt in [...OPCOES_DECISIVO, 'Outro']"
                :key="opt"
                :text="opt"
                :selected="form.decisivo_prospeccao.includes(opt)"
                multi
                @click="toggleChip(form.decisivo_prospeccao, opt)"
              />
            </div>
            <input v-if="form.decisivo_prospeccao.includes('Outro')" v-model="form.decisivo_prospeccao_outro" placeholder="Descreva o que foi decisivo..." v-bind="inputClass" class="mt-3" />
          </ObField>
        </ObCard>

        <ObCard title="Experiência na reunião de diagnóstico">
          <ObField label="Qual frase descreve melhor sua experiência na reunião?">
            <div class="space-y-2">
              <ObOptRow
                v-for="opt in [...OPCOES_REUNIAO, 'Outro']"
                :key="opt"
                :text="opt"
                :selected="form.experiencia_reuniao.includes(opt)"
                multi
                @click="toggleChip(form.experiencia_reuniao, opt)"
              />
            </div>
            <input v-if="form.experiencia_reuniao.includes('Outro')" v-model="form.experiencia_reuniao_outro" placeholder="Descreva sua experiência..." v-bind="inputClass" class="mt-3" />
          </ObField>
        </ObCard>

        <ObCard title="Indicador de sucesso">
          <ObField label="Ao final do projeto, qual indicador fará você dizer que valeu a pena?">
            <div class="space-y-2">
              <ObOptRow v-for="opt in [...OPCOES_SUCESSO, 'Outro']" :key="opt" :text="opt" :selected="form.indicador_sucesso === opt" @click="form.indicador_sucesso = form.indicador_sucesso === opt ? '' : opt" />
            </div>
            <input v-if="form.indicador_sucesso === 'Outro'" v-model="form.indicador_sucesso_outro" placeholder="Descreva o indicador..." v-bind="inputClass" class="mt-3" />
          </ObField>
        </ObCard>
      </div>

      <!-- ══════ STEP 8 — GERAR ══════ -->
      <div v-show="step === 8">
        <ObStepHeader tag="Etapa 8 de 8" title="Revisão e envio" desc="Confirme os dados e sincronize com o Pipedrive." />

        <!-- Regras obrigatórias -->
        <div v-if="rules.length" class="bg-amber-400/5 ring-1 ring-amber-400/10 rounded-2xl p-4 mb-6">
          <p class="text-xs font-semibold text-amber-300/60 uppercase tracking-widest mb-3">
            Confirme antes de sincronizar
          </p>
          <div class="space-y-3">
            <label
              v-for="rule in rules"
              :key="rule.id"
              class="flex items-start gap-3 cursor-pointer group"
            >
              <input
                type="checkbox"
                :checked="rule.checked"
                class="mt-0.5 w-4 h-4 accent-amber-400 shrink-0 cursor-pointer"
                @change="onToggleRule(rule)"
              />
              <span class="min-w-0">
                <span class="block text-sm text-white/80 font-medium">{{ rule.name }}</span>
                <span class="block text-xs text-white/50 leading-relaxed mt-0.5" v-html="renderRichText(rule.content)" />
              </span>
            </label>
          </div>
        </div>

        <div class="bg-blue-400/5 ring-1 ring-blue-400/10 rounded-2xl p-4 mb-6 text-sm text-blue-300/80 leading-relaxed">
          Ao clicar em <strong class="text-blue-300">Finalizar e Sincronizar</strong>, uma nota com o briefing completo será criada no deal do Pipedrive.
        </div>

        <!-- Resumo -->
        <ObCard title="Negócio">
          <ObSummaryRow k="Empresa" :v="form.nome_empresa" />
          <ObSummaryRow k="Nicho" :v="form.nicho" />
          <ObSummaryRow k="Ticket médio" :v="form.ticket" />
          <ObSummaryRow k="Tipo de venda" :v="form.tipo_venda" />
        </ObCard>

        <ObCard title="Lead">
          <ObSummaryRow k="Perfil ICP" :v="form.perfil_lead" />
          <ObSummaryRow k="Tom de comunicação" :v="form.tom.join(', ')" />
        </ObCard>

        <ObCard title="Funis">
          <ObSummaryRow k="Funis ativos" :v="form.funis.join(', ') || '—'" />
        </ObCard>

        <ObCard title="Fechamento">
          <ObSummaryRow k="Plano" :v="form.plano_selecionado.toUpperCase() || '—'" />
        </ObCard>

        <div v-if="status === 'synced'" class="mt-6 flex items-center gap-3 p-4 bg-emerald-400/5 ring-1 ring-emerald-400/10 rounded-2xl">
          <svg class="w-5 h-5 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          <span class="text-sm text-emerald-300">Sincronizado com o Pipedrive com sucesso.</span>
        </div>

        <!-- ── Materiais IA ── -->
        <div class="mt-10 border-t border-white/[0.06] pt-8">
          <h3 class="text-base font-semibold text-white mb-1">Materiais gerados por IA</h3>
          <p class="text-sm text-white/40 mb-6">Script CRM, material de fechamento e roteiro de qualificação personalizados para o cliente.</p>

          <!-- quality alerts -->
          <div v-if="materials?.quality_alerts?.length" class="mb-6 p-4 bg-amber-400/5 ring-1 ring-amber-400/10 rounded-2xl">
            <p class="text-xs font-semibold text-amber-300/60 uppercase tracking-widest mb-2">Atenção — campos incompletos podem deixar o material genérico</p>
            <ul class="space-y-1.5">
              <li v-for="alert in materials.quality_alerts" :key="alert" class="flex items-start gap-2 text-sm text-amber-300/70">
                <span class="shrink-0 mt-0.5">⚠</span>
                <span>{{ alert }}</span>
              </li>
            </ul>
          </div>

          <!-- idle / failed: generate button -->
          <div v-if="!materials || materials.status === 'failed'" class="flex flex-col items-center py-12 gap-4">
            <p v-if="materials?.status === 'failed'" class="text-red-400/70 text-sm text-center max-w-md">
              {{ materials.error || 'Falha na geração. Tente novamente.' }}
            </p>
            <button
              class="px-8 py-3 bg-white text-neutral-900 text-sm font-semibold rounded-full hover:-translate-y-0.5 transition-all disabled:opacity-40 flex items-center gap-2"
              :disabled="materialsGenerating || creatingMaterial"
              @click="createModalOpen = true"
            >
              <svg v-if="materialsGenerating || creatingMaterial" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ materialsGenerating ? 'Iniciando...' : creatingMaterial ? 'Criando...' : '✦ Criar material' }}
            </button>
            <p class="text-xs text-white/30">IA, em branco ou copiar de outro onboarding</p>
          </div>

          <!-- pending / running: spinner -->
          <div v-else-if="materials.status === 'pending' || materials.status === 'running'" class="flex flex-col items-center py-16 gap-4">
            <svg class="w-8 h-8 text-white/30 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <p class="text-white/40 text-sm">Gerando materiais... (~20–30s)</p>
          </div>

          <!-- complete: open in new tab -->
          <div v-else-if="materials.status === 'complete'" class="flex flex-col items-center py-10 gap-5">
            <div class="w-12 h-12 rounded-full bg-emerald-400/10 ring-1 ring-emerald-400/20 flex items-center justify-center">
              <svg class="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
            </div>
            <div class="text-center">
              <p class="text-sm font-medium text-white/80 mb-1">Materiais gerados com sucesso</p>
              <p class="text-xs text-white/30">Script CRM, fechamento e qualificação prontos para editar</p>
            </div>
            <div class="flex gap-3">
              <button
                class="px-6 py-2.5 bg-white text-neutral-900 text-sm font-semibold rounded-full hover:-translate-y-0.5 transition-all flex items-center gap-2"
                @click="openMaterials"
              >
                Abrir Materiais
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                </svg>
              </button>
              <button
                class="px-4 py-2.5 text-sm text-white/40 hover:text-white/70 border border-white/10 rounded-full transition-all"
                :disabled="materialsGenerating"
                @click="generateMaterials"
              >
                Regenerar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Nav footer -->
      <div class="fixed bottom-0 left-14 right-0 bg-[#0a0a0a]/80 backdrop-blur-xl border-t border-white/[0.06] px-8 py-4">
        <div class="max-w-3xl mx-auto flex items-center justify-between">
          <button
            v-if="step > 1"
            class="px-5 py-2 text-sm text-white/50 hover:text-white/80 border border-white/10 rounded-full transition-all"
            @click="prevStep"
          >
            ← Voltar
          </button>
          <div v-else />

          <button
            v-if="step < 8"
            class="px-6 py-2 bg-white text-neutral-900 text-sm font-semibold rounded-full hover:-translate-y-0.5 transition-all disabled:opacity-40"
            :disabled="saving"
            @click="nextStep"
          >
            {{ saving ? 'Salvando...' : 'Próximo →' }}
          </button>
          <button
            v-else-if="status !== 'synced'"
            class="px-6 py-2 bg-white text-neutral-900 text-sm font-semibold rounded-full hover:-translate-y-0.5 transition-all disabled:opacity-40 flex items-center gap-2"
            :disabled="submitting || pendingRules"
            :title="pendingRules ? 'Confirme todas as regras antes de sincronizar' : ''"
            @click="submitGuarded"
          >
            <svg v-if="submitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ submitting ? 'Sincronizando...' : '✦ Finalizar e Sincronizar' }}
          </button>
        </div>
      </div>
    </div>

    <ObCreateMaterialModal
      :open="createModalOpen"
      :loading="creatingMaterial || materialsGenerating"
      :load-library="loadMaterialLibrary"
      @close="createModalOpen = false"
      @create="handleCreateMaterial"
    />
  </div>
</template>

<script setup lang="ts">
import type { RuleWithAck } from '~/composables/useRules'

const route = useRoute()
const id = route.params.id as string

const {
  form, step, saving, submitting, loading, status, dealId, dealName,
  load, nextStep, prevStep, submit,
  toggleChip, toggleFunil, selectPlano, addEtapa, addBonus, moveInList,
  addEtapaFechamento, removeEtapaFechamento, moveEtapaFechamento,
  PLANOS,
  materials, materialsGenerating, loadMaterials, generateMaterials,
  createManualMaterial, copyMaterialFrom, loadMaterialLibrary,
  suggestingScripts, suggestScripts,
} = useOnboarding(id)

const createModalOpen = ref(false)
const creatingMaterial = ref(false)
const showFechExtra = ref(false)
const router = useRouter()

// ── Regras de onboarding ──
const { loadOnboardingRules, toggleAck } = useRules()
const rules = ref<RuleWithAck[]>([])
const pendingRules = computed(() => rules.value.some(r => !r.checked))

const onToggleRule = async (rule: RuleWithAck) => {
  const prev = rule.checked
  rule.checked = !prev
  try {
    const res = await toggleAck(id, rule.id)
    rule.checked = res.checked
  } catch {
    rule.checked = prev
    alert('Falha ao registrar confirmação.')
  }
}

const submitGuarded = async () => {
  try {
    await submit()
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || 'Erro ao sincronizar')
  }
}

const handleCreateMaterial = async (payload: { mode: 'ai' | 'blank' | 'copy'; sourceId?: number }) => {
  creatingMaterial.value = true
  try {
    if (payload.mode === 'ai') {
      createModalOpen.value = false
      await generateMaterials()
    } else if (payload.mode === 'blank') {
      await createManualMaterial()
      createModalOpen.value = false
      router.push(`/onboarding/${id}/materials`)
    } else if (payload.mode === 'copy' && payload.sourceId) {
      await copyMaterialFrom(payload.sourceId)
      createModalOpen.value = false
      router.push(`/onboarding/${id}/materials`)
    }
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || 'Erro ao criar material')
  } finally {
    creatingMaterial.value = false
  }
}

const STATUS_LABEL: Record<string, string> = {
  draft: 'Rascunho',
  complete: 'Concluído',
  synced: 'Sincronizado',
}

const STEP_LABELS = ['Negócio', 'Lead', 'Funis', 'Fechamento', 'Scripts', 'Datas', 'Pesquisa', 'Gerar']

const FUNIS = [
  { key: 'trafego',    name: 'Tráfego Pago',          desc: 'Meta Ads, Google, TikTok' },
  { key: 'prospeccao', name: 'Prospecção Ativa',        desc: 'SDR aborda leads frios' },
  { key: 'social',     name: 'Social Selling',          desc: 'Engajamento no Instagram/LinkedIn' },
  { key: 'carteira',   name: 'Carteira / Reativação',   desc: 'Leads antigos ou perdidos' },
  { key: 'posvenda',   name: 'Pós-venda / Indicação',   desc: 'Clientes fechados, indicações' },
  { key: 'custom',     name: 'Funil Customizado',        desc: 'Lógica diferente dos acima' },
]

const OPCOES_DECISIVO = [
  'A abordagem foi 100% personalizada — ele provou que estudou meu negócio antes de entrar em contato',
  'O SDR demonstrou uma técnica de comunicação superior à da minha própria equipe',
  'Ele tocou em um ponto cego da minha operação que me gerou curiosidade imediata',
  'A cadência de follow-up foi impecável — soube insistir sem ser chato',
  'Não tentou vender — ofereceu um insight que valia meu tempo',
  'Não vi nada demais',
]

const OPCOES_REUNIAO = [
  'O especialista identificou um gargalo que eu nem sabia que existia',
  'Apresentei uma objeção difícil e ele contornou com argumento lógico que me convenceu',
  'Ele desenhou o ROI de forma tão clara que o investimento pareceu barato',
  'Senti que ele entendia mais do meu processo comercial do que eu',
  'Ele desafiou minha visão e me fez perceber que eu continuaria perdendo dinheiro sem mudar',
  'Já estava comprado antes de entrar na reunião',
]

const OPCOES_SUCESSO = [
  'ROI — o aumento de faturamento pagou a assessoria e gerou lucro real no caixa',
  'Processos organizados — não dependemos mais de sorte ou caos para vender',
  'Saí do operacional de vendas e o time roda sem ficar me perguntando',
  'Área comercial profissional com método validado, independente do faturamento imediato',
]

const inputClass = {
  class: 'w-full px-3.5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors',
}
const textareaClass = {
  class: 'w-full px-3.5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-vertical',
  style: 'min-height:80px; line-height:1.6',
}
const metricInputClass = {
  class: 'w-full bg-transparent border-none text-white text-lg font-bold placeholder-white/10 focus:outline-none p-0',
}

const jumpTo = (n: number) => { step.value = n }
const openMaterials = () => window.open(`/onboarding/${id}/materials`, '_blank')

await load()
await loadMaterials()

// Placeholder (sem deal + material já completo) → redireciona pro editor
if (!dealId.value && materials.value?.status === 'complete') {
  await navigateTo(`/onboarding/${id}/materials`, { replace: true })
}

try { rules.value = await loadOnboardingRules(id) } catch { rules.value = [] }
</script>

