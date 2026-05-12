<template>
  <div class="min-h-screen bg-[#0a0a0a] transition-[padding] duration-200" :class="dataDrawerOpen ? 'sm:pr-[24rem]' : ''">
    <!-- Header sticky -->
    <div class="sticky top-0 z-20 bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-white/[0.06]">
      <div class="max-w-4xl mx-auto px-6 py-3 flex items-center justify-between gap-4">
        <!-- Voltar + nome -->
        <div class="flex items-center gap-3 min-w-0">
          <NuxtLink :to="`/onboarding/${id}`" class="text-white/30 hover:text-white/60 transition-colors shrink-0">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
            </svg>
          </NuxtLink>
          <div class="min-w-0">
            <p class="text-white text-sm font-medium truncate">{{ dealName || 'Materiais' }}</p>
            <p class="text-xs text-white/30">Script CRM · Fechamento · Qualificação</p>
          </div>
        </div>

        <!-- Ações -->
        <div class="flex items-center gap-3 shrink-0">
          <!-- indicador de save -->
          <template v-if="!isDesenvolvedor">
            <span v-if="saveStatus === 'saving'" class="flex items-center gap-1.5 text-xs text-white/30">
              <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Salvando...
            </span>
            <span v-else-if="saveStatus === 'saved'" class="text-xs text-emerald-400/70">Salvo</span>
          </template>

          <!-- Dropdown exportar PDF -->
          <div ref="pdfDropdownRef" class="relative">
            <button
              class="px-3 py-1.5 text-sm text-white/50 hover:text-white/80 border border-white/10 rounded-lg transition-all flex items-center gap-1.5"
              @click.stop="pdfMenuOpen = !pdfMenuOpen"
            >
              Exportar PDF
              <svg class="w-3 h-3 transition-transform" :class="pdfMenuOpen ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
              </svg>
            </button>
            <div
              v-show="pdfMenuOpen"
              class="absolute right-0 top-full mt-1 bg-neutral-900 ring-1 ring-white/10 rounded-xl py-1 min-w-44 z-50 shadow-xl"
            >
              <a
                v-for="opt in PDF_OPTS"
                :key="opt.key"
                :href="opt.key === 'crm' ? `/onboarding/${id}/print-crm` : `/onboarding/${id}/print?section=${opt.key}`"
                target="_blank"
                class="flex items-center gap-2 px-3 py-2.5 text-sm text-white/60 hover:text-white hover:bg-white/5 transition-colors"
                @click="pdfMenuOpen = false"
              >
                {{ opt.label }}
              </a>
            </div>
          </div>
          <button
            v-if="!isDesenvolvedor"
            class="px-3 py-1.5 text-sm text-white/50 hover:text-white/80 border border-white/10 rounded-lg transition-all disabled:opacity-40"
            :disabled="materialsGenerating"
            @click="handleRegenerate"
          >
            {{ materialsGenerating ? 'Gerando...' : 'Regenerar' }}
          </button>
          <button
            v-if="!isDesenvolvedor && materials?.status === 'complete'"
            class="px-3 py-1.5 text-sm rounded-lg transition-all disabled:opacity-40"
            :class="materials?.published
              ? 'bg-emerald-500/10 text-emerald-300 ring-1 ring-emerald-500/30 hover:bg-emerald-500/15'
              : 'bg-white text-neutral-900 hover:bg-white/90'"
            :disabled="publishing"
            @click="handlePublish"
          >
            <span v-if="publishing">...</span>
            <span v-else-if="materials?.published" class="flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              Publicado
            </span>
            <span v-else>Publicar</span>
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-6 py-8 pb-24">

      <!-- Generating state -->
      <div v-if="generating" class="flex flex-col items-center py-24 gap-4">
        <svg class="w-8 h-8 text-white/30 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        <p class="text-white/40 text-sm">Regenerando materiais... (~20–30s)</p>
      </div>

      <!-- Not generated -->
      <div v-else-if="!materials || materials.status !== 'complete'" class="flex flex-col items-center py-24 gap-4">
        <p class="text-white/40 text-sm">Material ainda não gerado.</p>
        <div class="flex items-center gap-3">
          <button
            v-if="!isDesenvolvedor"
            class="bg-white text-neutral-900 text-sm font-medium px-5 py-2 rounded-full hover:bg-white/90 transition-colors"
            @click="createModalOpen = true"
          >
            Criar material
          </button>
          <NuxtLink :to="`/onboarding/${id}`" class="text-sm text-white/60 underline underline-offset-4">Voltar ao formulário</NuxtLink>
        </div>
      </div>

      <!-- Content -->
      <template v-else-if="editedMaterials">

        <!-- Quality alerts banner (colapsável) -->
        <div v-if="materials.quality_alerts?.length" class="mb-6 bg-amber-400/5 ring-1 ring-amber-400/10 rounded-2xl overflow-hidden">
          <button
            class="w-full flex items-center justify-between px-4 py-3 text-sm text-amber-300/70 hover:text-amber-300/90 transition-colors"
            @click="alertsOpen = !alertsOpen"
          >
            <span class="flex items-center gap-2 font-medium">
              <span>⚠</span>
              {{ materials.quality_alerts.length }} alerta{{ materials.quality_alerts.length > 1 ? 's' : '' }} de qualidade
            </span>
            <svg class="w-4 h-4 transition-transform" :class="alertsOpen ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
            </svg>
          </button>
          <div v-show="alertsOpen" class="border-t border-amber-400/10 px-4 py-3 space-y-2">
            <p v-for="alert in materials.quality_alerts" :key="alert" class="text-sm text-amber-300/60 flex gap-2">
              <span class="shrink-0">·</span>
              <span>{{ alert }}</span>
            </p>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex items-center justify-between mb-6 gap-3 flex-wrap">
          <div class="flex gap-1 p-1 bg-white/5 rounded-xl w-fit">
            <button
              v-for="t in TABS"
              :key="t.key"
              class="px-5 py-2 rounded-lg text-sm font-medium transition-all"
              :class="activeTab === t.key ? 'bg-white text-neutral-900' : 'text-white/50 hover:text-white/80'"
              @click="activeTab = t.key as any"
            >
              {{ t.label }}
            </button>
          </div>

        </div>

        <!-- ── CRM ── -->
        <div v-show="activeTab === 'crm'" :inert="isDesenvolvedor || undefined">

          <!-- Seletor de funil -->
          <div class="flex items-center gap-2 flex-wrap mb-4 pb-4 border-b border-white/[0.06]">
            <span class="text-xs font-semibold text-white/40 uppercase tracking-widest mr-1">Funil:</span>
            <button
              v-for="(funnel, fi) in editedMaterials.crm!.funnels"
              :key="fi"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all"
              :class="activeFunnel === fi
                ? 'bg-white text-neutral-900'
                : 'text-white/50 hover:text-white/80 bg-white/5 ring-1 ring-white/10'"
              @click="activeFunnel = fi; activeStage = 0"
            >
              {{ funnel.name || funnel.key || 'Funil ' + (fi + 1) }}
            </button>
            <button
              v-if="!isDesenvolvedor"
              class="flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium text-white/40 hover:text-white/70 border border-dashed border-white/15 hover:border-white/30 transition-all"
              @click="addFunnel"
            >
              + Funil
            </button>
          </div>

          <div v-if="!editedMaterials.crm!.funnels.length" class="bg-white/[0.03] ring-1 ring-white/[0.08] rounded-2xl p-10 text-center">
            <p class="text-sm text-white/40 mb-3">Nenhum funil ainda.</p>
            <button
              v-if="!isDesenvolvedor"
              class="text-sm text-white/70 underline underline-offset-4 hover:text-white"
              @click="addFunnel"
            >
              Adicionar primeiro funil
            </button>
          </div>

          <template v-else-if="currentFunnel">

          <!-- Header do funil ativo -->
          <div class="flex items-center gap-3 mb-5 bg-white/[0.03] ring-1 ring-white/[0.08] rounded-xl px-4 py-2.5">
            <input
              v-model="currentFunnel.name"
              placeholder="Nome do funil"
              class="flex-1 bg-transparent text-sm font-semibold text-white placeholder-white/30 focus:outline-none"
            />
            <select
              v-model="currentFunnel.key"
              class="text-xs px-2 py-1 bg-white/5 rounded-lg text-white/60 border border-white/10 focus:outline-none"
            >
              <option value="trafego">trafego</option>
              <option value="prospeccao">prospeccao</option>
              <option value="social">social</option>
              <option value="carteira">carteira</option>
              <option value="posvenda">posvenda</option>
              <option value="custom">custom</option>
              <option value="default">default</option>
            </select>
            <button
              v-if="!isDesenvolvedor"
              type="button"
              title="Excluir funil"
              class="text-white/30 hover:text-red-400/70 transition-colors shrink-0"
              @click="removeFunnel(activeFunnel)"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166M5.79 5.79c.34-.06.68-.114 1.022-.166m0 0a48.108 48.108 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
              </svg>
            </button>
          </div>

          <!-- Seletor de etapa -->
          <div class="flex gap-1 flex-wrap mb-5">
            <button
              v-for="(stage, si) in currentFunnel.stages"
              :key="si"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
              :class="activeStage === si
                ? 'bg-white/10 text-white ring-1 ring-white/20'
                : 'text-white/40 hover:text-white/70 hover:bg-white/5'"
              @click="activeStage = si"
            >
              <span class="text-white/30">{{ si + 1 }}</span>
              {{ stage.name || 'Etapa ' + (si + 1) }}
            </button>
            <button
              v-if="!isDesenvolvedor"
              class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-white/40 hover:text-white/70 border border-dashed border-white/15 hover:border-white/30 transition-all"
              @click="addCrmStage"
            >
              + Etapa
            </button>
          </div>

          <div v-if="!currentFunnel.stages.length" class="bg-white/[0.03] ring-1 ring-white/[0.08] rounded-2xl p-10 text-center">
            <p class="text-sm text-white/40 mb-3">Nenhuma etapa nesse funil.</p>
            <button
              v-if="!isDesenvolvedor"
              class="text-sm text-white/70 underline underline-offset-4 hover:text-white"
              @click="addCrmStage"
            >
              Adicionar primeira etapa
            </button>
          </div>

          <!-- Conteúdo da etapa selecionada -->
          <template v-if="currentFunnel.stages[activeStage]">
            <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5 space-y-5">
              <!-- Nome + delete -->
              <div class="flex items-center gap-3">
                <span class="text-xs font-bold text-white/20 w-5 text-center shrink-0">{{ activeStage + 1 }}</span>
                <input
                  v-model="currentFunnel!.stages[activeStage].name"
                  placeholder="Nome da etapa"
                  class="flex-1 bg-transparent text-base font-semibold text-white placeholder-white/20 focus:outline-none border-b border-white/10 pb-1"
                />
                <button
                  v-if="!isDesenvolvedor"
                  type="button"
                  title="Excluir etapa"
                  class="text-white/30 hover:text-red-400/70 transition-colors shrink-0"
                  @click="removeCrmStage(activeStage)"
                >
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                  </svg>
                </button>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-white/30 mb-1.5">Objetivo</p>
                  <textarea v-model="currentFunnel!.stages[activeStage].objective" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
                </div>
                <div>
                  <p class="text-xs text-white/30 mb-1.5">Critério de avanço</p>
                  <textarea v-model="currentFunnel!.stages[activeStage].advance_criteria" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
                </div>
              </div>

              <div>
                <p class="text-xs text-white/20 mb-1.5">Instruções para o dev</p>
                <textarea v-model="currentFunnel!.stages[activeStage].dev_instructions" class="w-full px-3 py-2 bg-white/[0.02] border border-white/[0.06] rounded-xl text-xs text-white/40 focus:outline-none focus:border-white/10 transition-colors resize-y" rows="3" />
              </div>

              <!-- Cadência -->
              <div class="border-t border-white/[0.06] pt-4">
                <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-4">Cadência</p>
                <div
                  v-for="(day, di) in currentFunnel!.stages[activeStage].cadence"
                  :key="di"
                  class="mb-5"
                >
                  <div class="flex items-center justify-between mb-3 gap-2">
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-bold text-white/30">Dia</span>
                      <input
                        v-model.number="day.day"
                        type="number"
                        min="0"
                        class="w-14 px-2 py-1 bg-white/[0.04] border border-white/10 rounded-lg text-xs text-white focus:outline-none focus:border-white/20"
                      />
                    </div>
                    <button
                      v-if="!isDesenvolvedor"
                      type="button"
                      class="text-white/20 hover:text-red-400/60 transition-colors text-lg shrink-0"
                      @click="currentFunnel!.stages[activeStage].cadence.splice(di, 1)"
                    >×</button>
                  </div>
                  <div v-for="(action, ai) in day.actions" :key="ai" class="mb-4 pl-4 border-l border-white/[0.08] space-y-2">
                    <div class="flex items-center justify-between gap-2">
                      <select
                        v-model="action.channel"
                        class="text-xs px-2 py-1 bg-white/5 rounded-full text-white/60 capitalize border border-white/[0.06] focus:outline-none"
                      >
                        <option value="whatsapp">whatsapp</option>
                        <option value="ligacao">ligação</option>
                        <option value="email">email</option>
                        <option value="sms">sms</option>
                        <option value="atividade">atividade</option>
                      </select>
                      <button
                        v-if="!isDesenvolvedor"
                        type="button"
                        class="text-white/20 hover:text-red-400/60 transition-colors text-lg shrink-0"
                        @click="day.actions.splice(ai, 1)"
                      >×</button>
                    </div>
                    <textarea v-model="action.message" placeholder="Mensagem" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
                    <textarea v-if="action.instructions !== undefined" v-model="action.instructions" placeholder="Instruções" class="w-full px-3 py-2 bg-white/[0.02] border border-white/[0.06] rounded-xl text-xs text-white/40 focus:outline-none resize-y" rows="2" />
                  </div>
                  <button
                    v-if="!isDesenvolvedor"
                    type="button"
                    class="ml-4 text-xs text-white/40 hover:text-white/70 border border-dashed border-white/10 hover:border-white/20 rounded-lg px-3 py-1.5 transition-all"
                    @click="addCadenceAction(di)"
                  >
                    + Ação
                  </button>
                </div>
                <button
                  v-if="!isDesenvolvedor"
                  type="button"
                  class="w-full py-2.5 border border-dashed border-white/10 rounded-xl text-xs text-white/30 font-semibold tracking-widest uppercase hover:border-white/20 hover:text-white/50 transition-all"
                  @click="addCadenceDay"
                >
                  + Adicionar dia
                </button>
              </div>
            </div>

            <!-- Navegação entre etapas -->
            <div class="flex justify-between mt-4">
              <button
                v-if="activeStage > 0"
                class="flex items-center gap-2 px-4 py-2 text-sm text-white/40 hover:text-white/70 border border-white/10 rounded-xl transition-all"
                @click="activeStage--"
              >
                ← {{ currentFunnel!.stages[activeStage - 1].name || 'Anterior' }}
              </button>
              <div v-else />
              <button
                v-if="activeStage < currentFunnel!.stages.length - 1"
                class="flex items-center gap-2 px-4 py-2 text-sm text-white/40 hover:text-white/70 border border-white/10 rounded-xl transition-all"
                @click="activeStage++"
              >
                {{ currentFunnel!.stages[activeStage + 1].name || 'Próxima' }} →
              </button>
            </div>
          </template>

          </template>
        </div>

        <!-- ── Fechamento ── -->
        <div v-show="activeTab === 'fechamento'" class="space-y-4" :inert="isDesenvolvedor || undefined">
          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Perguntas de diagnóstico</p>
            <div v-for="(q, qi) in editedMaterials.closing!.diagnostic_questions" :key="qi" class="flex gap-2 mb-2">
              <textarea v-model="editedMaterials.closing!.diagnostic_questions[qi]" class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-y" rows="3" />
              <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg self-start mt-1 shrink-0" @click="editedMaterials.closing!.diagnostic_questions.splice(qi, 1)">×</button>
            </div>
            <button class="w-full py-2.5 border border-dashed border-white/10 rounded-xl text-xs text-white/30 font-semibold tracking-widest uppercase hover:border-white/20 hover:text-white/50 transition-all mt-1" @click="editedMaterials.closing!.diagnostic_questions.push('')">+ Adicionar pergunta</button>
          </div>

          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Apresentação de preço</p>
            <textarea v-model="editedMaterials.closing!.price_presentation" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-y" rows="8" />
          </div>

          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Matriz de objeções</p>
            <div class="grid grid-cols-3 gap-2 mb-2 px-1">
              <p class="text-xs text-white/20">Objeção</p>
              <p class="text-xs text-white/20">Medo real</p>
              <p class="text-xs text-white/20">Contra-argumento</p>
            </div>
            <div v-for="(row, ri) in editedMaterials.closing!.objection_matrix" :key="ri" class="grid grid-cols-3 gap-2 mb-2 items-start">
              <textarea v-model="row.objection" class="px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
              <textarea v-model="row.hidden_concern" class="px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
              <div class="flex gap-1">
                <textarea v-model="row.counter_script" class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
                <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg self-start mt-1 shrink-0" @click="editedMaterials.closing!.objection_matrix.splice(ri, 1)">×</button>
              </div>
            </div>
            <button class="w-full py-2.5 border border-dashed border-white/10 rounded-xl text-xs text-white/30 font-semibold tracking-widest uppercase hover:border-white/20 hover:text-white/50 transition-all" @click="editedMaterials.closing!.objection_matrix.push({ objection: '', hidden_concern: '', counter_script: '' })">+ Adicionar objeção</button>
          </div>

          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Script de fechamento</p>
            <textarea v-model="editedMaterials.closing!.closing_script" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-y" rows="16" />
          </div>

          <div v-if="editedMaterials.closing!.special_condition" class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Condição especial</p>
            <textarea v-model="editedMaterials.closing!.special_condition" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
          </div>
        </div>

        <!-- ── Qualificação ── -->
        <div v-show="activeTab === 'qualificacao'" class="space-y-4" :inert="isDesenvolvedor || undefined">
          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <div class="flex items-center justify-between mb-3 gap-2">
              <p class="text-xs font-semibold text-white/30 uppercase tracking-widest">Fluxo WhatsApp</p>
              <select
                v-model="editedMaterials.qualification!.profile"
                class="text-xs px-2.5 py-1 bg-white/5 rounded-full text-white/70 uppercase border border-white/[0.06] focus:outline-none focus:border-white/20 cursor-pointer"
              >
                <option value="b2b">B2B</option>
                <option value="b2c">B2C</option>
              </select>
            </div>
            <div v-for="(s, si) in editedMaterials.qualification!.whatsapp_flow" :key="si" class="mb-3 flex gap-3 items-start">
              <div class="shrink-0 pt-2">
                <span class="text-xs px-2 py-0.5 bg-white/5 rounded-full text-white/40 capitalize block text-center">{{ s.type }}</span>
                <span v-if="s.channel" class="text-xs text-white/20 block text-center mt-1">{{ s.channel }}</span>
              </div>
              <textarea v-model="s.content" class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
              <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg mt-2 shrink-0" @click="editedMaterials.qualification!.whatsapp_flow.splice(si, 1)">×</button>
            </div>
            <button class="w-full py-2.5 border border-dashed border-white/10 rounded-xl text-xs text-white/30 font-semibold tracking-widest uppercase hover:border-white/20 hover:text-white/50 transition-all" @click="editedMaterials.qualification!.whatsapp_flow.push({ type: 'message', content: '' })">+ Adicionar step</button>
          </div>

          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Pitch de ligação</p>
            <textarea v-model="editedMaterials.qualification!.call_pitch" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-y" rows="12" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
              <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Critérios de avanço</p>
              <div v-for="(c, ci) in editedMaterials.qualification!.advance_criteria" :key="ci" class="flex gap-2 mb-2">
                <textarea v-model="editedMaterials.qualification!.advance_criteria[ci]" class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="4" />
                <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg self-start mt-1 shrink-0" @click="editedMaterials.qualification!.advance_criteria.splice(ci, 1)">×</button>
              </div>
              <button class="w-full py-2 border border-dashed border-white/10 rounded-xl text-xs text-white/30 hover:border-white/20 hover:text-white/50 transition-all" @click="editedMaterials.qualification!.advance_criteria.push('')">+ Adicionar</button>
            </div>

            <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
              <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Critérios de desqualificação</p>
              <div v-for="(c, ci) in editedMaterials.qualification!.disqualification_criteria" :key="ci" class="flex gap-2 mb-2">
                <textarea v-model="editedMaterials.qualification!.disqualification_criteria[ci]" class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="4" />
                <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg self-start mt-1 shrink-0" @click="editedMaterials.qualification!.disqualification_criteria.splice(ci, 1)">×</button>
              </div>
              <button class="w-full py-2 border border-dashed border-white/10 rounded-xl text-xs text-white/30 hover:border-white/20 hover:text-white/50 transition-all" @click="editedMaterials.qualification!.disqualification_criteria.push('')">+ Adicionar</button>
            </div>
          </div>
        </div>

      </template>
    </div>

    <!-- Botões flutuantes: toggle painéis -->
    <div
      v-if="materials && materials.status === 'complete' && !dataDrawerOpen && !assistantOpen"
      class="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-2"
    >
      <button
        v-if="!isDesenvolvedor"
        type="button"
        class="flex items-center gap-2 bg-emerald-400/15 hover:bg-emerald-400/25 backdrop-blur-xl ring-1 ring-emerald-400/30 text-emerald-200 text-sm font-medium px-4 py-2.5 rounded-full transition-colors shadow-xl"
        @click="assistantOpen = true"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
        </svg>
        Assistente IA
      </button>
      <button
        type="button"
        class="flex items-center gap-2 bg-white/10 hover:bg-white/15 backdrop-blur-xl ring-1 ring-white/15 text-white text-sm font-medium px-4 py-2.5 rounded-full transition-colors shadow-xl"
        @click="dataDrawerOpen = true"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 0 1 0 3.75H5.625a1.875 1.875 0 0 1 0-3.75Z" />
        </svg>
        Ver dados
      </button>
    </div>

    <ObCreateMaterialModal
      :open="createModalOpen"
      :loading="creatingMaterial"
      :load-library="loadMaterialLibrary"
      @close="createModalOpen = false"
      @create="handleCreate"
    />

    <ObDataDrawer
      :open="dataDrawerOpen"
      :form="form"
      :deal-name="dealName"
      :assessor-name="assessorName"
      @close="dataDrawerOpen = false"
    />

    <ObAssistantPanel
      :open="assistantOpen"
      :onboarding-id="id"
      :material="editedMaterials"
      :section="assistantSection"
      :focus="assistantFocus"
      :focus-label="assistantFocusLabel"
      @close="assistantOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import type { MaterialOut } from '~/composables/useOnboarding'

definePageMeta({ layout: false })

const route = useRoute()
const id = route.params.id as string

const {
  materials, materialsGenerating, loadMaterials, generateMaterials, saveMaterials,
  createManualMaterial, copyMaterialFrom, loadMaterialLibrary, prepareAssistant,
  publishMaterial, dealName, assessorName, load, form,
} = useOnboarding(id)

const publishing = ref(false)
const handlePublish = async () => {
  if (publishing.value) return
  if (materials.value?.published && !confirm('Despublicar este material? Devs não conseguirão mais visualizá-lo.')) return
  publishing.value = true
  try { await publishMaterial() } finally { publishing.value = false }
}

const { user } = useAuth()
const isDesenvolvedor = computed(() => user.value?.roles?.includes('Desenvolvedor') && !user.value?.is_superuser)

const activeTab = ref<'crm' | 'fechamento' | 'qualificacao'>('crm')
const activeFunnel = ref(0)
const activeStage = ref(0)

const currentFunnel = computed(() => editedMaterials.value?.crm?.funnels[activeFunnel.value] ?? null)

const FUNIL_LABELS: Record<string, string> = {
  trafego: 'Tráfego Pago',
  prospeccao: 'Prospecção Ativa',
  social: 'Social Selling',
  carteira: 'Carteira / Reativação',
  posvenda: 'Pós-venda / Indicação',
  custom: 'Funil Customizado',
  default: 'Pipeline',
}

function addFunnel() {
  if (!editedMaterials.value?.crm) return
  const used = new Set(editedMaterials.value.crm.funnels.map(f => f.key))
  const next = (Object.keys(FUNIL_LABELS) as string[]).find(k => !used.has(k)) || 'custom'
  editedMaterials.value.crm.funnels.push({
    key: next,
    name: FUNIL_LABELS[next] || 'Novo funil',
    stages: [],
  })
  activeFunnel.value = editedMaterials.value.crm.funnels.length - 1
  activeStage.value = 0
}

function removeFunnel(i: number) {
  if (!editedMaterials.value?.crm) return
  if (!confirm('Excluir este funil e todas as etapas?')) return
  editedMaterials.value.crm.funnels.splice(i, 1)
  activeFunnel.value = Math.max(0, Math.min(activeFunnel.value, editedMaterials.value.crm.funnels.length - 1))
  activeStage.value = 0
}
const alertsOpen = ref(false)
const pdfMenuOpen = ref(false)
const pdfDropdownRef = ref<HTMLElement | null>(null)

const PDF_OPTS = [
  { key: 'crm', label: 'Script CRM' },
  { key: 'fechamento', label: 'Fechamento' },
  { key: 'qualificacao', label: 'Qualificação' },
]
const editedMaterials = ref<MaterialOut | null>(null)
const saveStatus = ref<'idle' | 'saving' | 'saved'>('idle')
const generating = ref(false)

const TABS = [
  { key: 'crm', label: 'CRM' },
  { key: 'fechamento', label: 'Fechamento' },
  { key: 'qualificacao', label: 'Qualificação' },
]

let _initialized = false
let _saveTimer: ReturnType<typeof setTimeout> | null = null

function normalizeMaterial(m: MaterialOut): MaterialOut {
  const copy = JSON.parse(JSON.stringify(m)) as MaterialOut
  if (!copy.crm || typeof copy.crm !== 'object') copy.crm = { funnels: [] }
  // Migra formato antigo (stages[] solto) para funnels[]
  const legacy = (copy.crm as any).stages
  if (Array.isArray(legacy) && !Array.isArray((copy.crm as any).funnels)) {
    copy.crm = { funnels: legacy.length ? [{ key: 'default', name: 'Pipeline', stages: legacy }] : [] }
  }
  if (!Array.isArray(copy.crm.funnels)) copy.crm.funnels = []
  if (!copy.closing || typeof copy.closing !== 'object') {
    copy.closing = { diagnostic_questions: [], price_presentation: '', objection_matrix: [], closing_script: '' }
  } else {
    copy.closing.diagnostic_questions ??= []
    copy.closing.price_presentation ??= ''
    copy.closing.objection_matrix ??= []
    copy.closing.closing_script ??= ''
  }
  if (!copy.qualification || typeof copy.qualification !== 'object') {
    copy.qualification = { profile: '', whatsapp_flow: [], call_pitch: '', advance_criteria: [], disqualification_criteria: [] }
  } else {
    copy.qualification.profile ??= ''
    copy.qualification.whatsapp_flow ??= []
    copy.qualification.call_pitch ??= ''
    copy.qualification.advance_criteria ??= []
    copy.qualification.disqualification_criteria ??= []
  }
  return copy
}

watch(materials, (m) => {
  if (m?.status === 'complete') {
    _initialized = false
    editedMaterials.value = normalizeMaterial(m)
    nextTick(() => { _initialized = true })
  }
}, { immediate: true })

watch(editedMaterials, () => {
  if (!_initialized || !editedMaterials.value || isDesenvolvedor.value) return
  saveStatus.value = 'saving'
  if (_saveTimer) clearTimeout(_saveTimer)
  _saveTimer = setTimeout(async () => {
    if (!editedMaterials.value) return
    await saveMaterials({
      crm: editedMaterials.value.crm,
      closing: editedMaterials.value.closing,
      qualification: editedMaterials.value.qualification,
    })
    saveStatus.value = 'saved'
    setTimeout(() => { saveStatus.value = 'idle' }, 2000)
  }, 1000)
}, { deep: true })

const handleRegenerate = async () => {
  generating.value = true
  await generateMaterials()
  generating.value = false
}

const createModalOpen = ref(false)
const dataDrawerOpen = ref(false)
const assistantOpen = ref(false)
const creatingMaterial = ref(false)

const assistantSection = computed<'crm' | 'closing' | 'qualification'>(() => {
  if (activeTab.value === 'fechamento') return 'closing'
  if (activeTab.value === 'qualificacao') return 'qualification'
  return 'crm'
})

const assistantFocus = computed(() => {
  if (assistantSection.value !== 'crm') return {}
  const f = currentFunnel.value
  if (!f) return {}
  return {
    funnel_key: f.key,
    stage_idx: f.stages.length ? activeStage.value : null,
  }
})

const assistantFocusLabel = computed(() => {
  if (assistantSection.value !== 'crm') return ''
  const f = currentFunnel.value
  if (!f) return ''
  const stage = f.stages[activeStage.value]
  return stage?.name ? `${f.name} · ${stage.name}` : f.name
})

watch(assistantOpen, (v) => { if (v) dataDrawerOpen.value = false })
watch(dataDrawerOpen, (v) => { if (v) assistantOpen.value = false })

watch(materials, (m) => {
  if (m?.status === 'complete') prepareAssistant()
}, { immediate: true })

function addCrmStage() {
  const funnel = currentFunnel.value
  if (!funnel) return
  funnel.stages.push({
    name: '', objective: '', dev_instructions: '', cadence: [],
    advance_criteria: '', loss_reason: '',
  })
  activeStage.value = funnel.stages.length - 1
}

function removeCrmStage(i: number) {
  const funnel = currentFunnel.value
  if (!funnel) return
  if (!confirm('Excluir esta etapa?')) return
  funnel.stages.splice(i, 1)
  activeStage.value = Math.max(0, Math.min(activeStage.value, funnel.stages.length - 1))
}

function addCadenceDay() {
  const stage = currentFunnel.value?.stages[activeStage.value]
  if (!stage) return
  const last = stage.cadence[stage.cadence.length - 1]
  stage.cadence.push({ day: last ? last.day + 1 : 0, actions: [] })
}

function addCadenceAction(dayIdx: number) {
  const stage = currentFunnel.value?.stages[activeStage.value]
  if (!stage) return
  stage.cadence[dayIdx].actions.push({ channel: 'whatsapp', message: '', instructions: '' })
}

const handleCreate = async (payload: { mode: 'ai' | 'blank' | 'copy'; sourceId?: number }) => {
  creatingMaterial.value = true
  try {
    if (payload.mode === 'ai') {
      createModalOpen.value = false
      generating.value = true
      await generateMaterials()
      generating.value = false
    } else if (payload.mode === 'blank') {
      await createManualMaterial()
      createModalOpen.value = false
    } else if (payload.mode === 'copy' && payload.sourceId) {
      await copyMaterialFrom(payload.sourceId)
      createModalOpen.value = false
    }
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || 'Erro ao criar material')
  } finally {
    creatingMaterial.value = false
  }
}

onMounted(async () => {
  await load()
  await loadMaterials()
  document.addEventListener('click', (e) => {
    if (pdfDropdownRef.value && !pdfDropdownRef.value.contains(e.target as Node)) {
      pdfMenuOpen.value = false
    }
  })
})
</script>
